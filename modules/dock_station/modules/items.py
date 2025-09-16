import re
import shutil  # наверху файла
from typing import TYPE_CHECKING, Literal
from difflib import get_close_matches
from fabric.widgets.button import Button
from gi.repository import GLib, Gdk, Gtk  # type:ignore
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.image import Image
from fabric.widgets.overlay import Overlay
from utils import JsonManager, IconResolver, setup_cursor_hover
from config import RESOLVED_ICONS, DOCK_STATION_PINS
from .actions import DockAction
from fabric.widgets.centerbox import CenterBox

if TYPE_CHECKING:
    from modules.dock_station.dock import Dock


class Items(Box):
    def __init__(self, cfg: "Dock"):
        self._cfg = cfg
        self.json = JsonManager()
        self.clients_cache: dict[str, list[dict]] = {}
        self.icons = IconResolver(RESOLVED_ICONS)
        self._pinned_order: list[str] = self._load_pins()
        self.icons_size = 38
        self.action = DockAction(self._cfg)
        self.pinned_list = self.json.get_data(DOCK_STATION_PINS)["pinned"]

        super().__init__(
            name="dock-station-items",
            orientation="h" if self._cfg.is_horizontal else "v",
        )

        GLib.idle_add(self.refresh)
        for ev in ("openwindow", "closewindow", "activewindow"):
            self._cfg.conn.connect(f"event::{ev}", self._on_windows_changed)

    def _on_windows_changed(self, *_):
        self.refresh()
        return True

    def _normalize(self, name: str) -> str:
        name = name.strip().lower()
        parts = re.split(r"[.\-_ ]+", name)
        ignore = {"com", "org", "project", "desktop", "launcher", "app"}
        parts = [p for p in parts if p and p not in ignore]
        if parts:
            return max(parts, key=len)
        return name

    def _correct_name(self, name: str) -> str:
        norm = self._normalize(name)
        for existing in self.clients_cache.keys():
            if self._normalize(existing) == norm:
                return existing
        matches = get_close_matches(
            norm,
            [self._normalize(k) for k in self.clients_cache.keys()],
            n=1,
            cutoff=0.6,
        )
        if matches:
            for existing in self.clients_cache.keys():
                if self._normalize(existing) == matches[0]:
                    return existing
        desktop_file = self.icons._get_desktop_file(name)
        if desktop_file:
            return desktop_file.split("/")[-1].removesuffix(".desktop")
        return name

    def _load_pins(self) -> list[str]:
        try:
            data = self.json.read(DOCK_STATION_PINS) or {}
            pins = data.get("pinned", [])
            corrected = []
            for p in pins:
                cname = self._correct_name(str(p))
                if cname not in corrected:
                    corrected.append(cname)
            return corrected
        except Exception:
            return []

    def get_clients(self) -> dict[str, list[dict]]:
        try:
            clients = self.json.loads(
                self._cfg.conn.send_command("j/clients").reply.decode()
            )
        except Exception:
            self.clients_cache = {}
            return self.clients_cache

        merged: dict[str, list[dict]] = {}
        for c in clients:
            cname = self._correct_name(c.get("class", "unknown"))
            merged.setdefault(cname, []).append(c)

        self.clients_cache = merged
        return self.clients_cache

    def clear_children(self):
        for child in list(self.get_children()):
            self.remove(child)

    def _create_item(
        self, app: str, instances: list[dict], show_empty: bool = False
    ) -> Button | None:
        count = len(instances)
        if count <= 0 and not show_empty:
            return None

        cmd = self.action._resolve_exec(app)
        if not shutil.which(cmd):
            return None

        icon = self.icons.get_icon_pixbuf(app, self.icons_size)
        image = Image(pixbuf=icon, name="dock-station-app-icons")

        children = [image]
        if count > 0:
            if self._cfg.instance_enabled:
                children.append(
                    Label(label=self._dots(count), name="dock-station-app-count")
                )

        inner_box = Box(
            name=f"dock-station-app-container", orientation="v", children=children
        )

        overlay = Overlay()
        overlay.add(inner_box)

        btn = Button(name=f"dock-station-app-buttons", child=overlay)
        setup_cursor_hover(btn)

        btn.connect(
            "button-press-event",
            lambda w, e: self.click_handler(w, e, inner_box, overlay, app, instances),
        )
        return btn

    def _render_items(self):
        pinned = []
        active = []
        for app in self._pinned_order:
            instances = self.clients_cache.get(app, [])
            item = self._create_item(app, instances, show_empty=True)
            if item:
                pinned.append(item)

        others = sorted(
            k for k in self.clients_cache.keys() if k not in self._pinned_order
        )
        for app in others:
            instances = self.clients_cache.get(app, [])
            item = self._create_item(app, instances)
            if item:
                active.append(item)

        line = Box(
            name="dock-station-app-line",
        )
        if self._cfg.is_horizontal:
            line.add_style_class("dock-station-app-line-horizontal")
            line.remove_style_class("dock-station-app-line-vertical")
        else:
            line.add_style_class("dock-station-app-line-vertical")
            line.remove_style_class("dock-station-app-line-horizontal")

        self.add(
            CenterBox(
                orientation="h" if self._cfg.is_horizontal else "v",
                start_children=active,
                center_children=line,
                end_children=pinned,
            )
        )

    def _dots(self, count: int) -> str:
        if not self._cfg.instance_enabled:
            return ""

        if count <= 0:
            return ""
        max_dots = self._cfg.max_dots
        return self._cfg.dots * min(count, max_dots)

    def refresh(self):
        self.get_clients()
        self.clear_children()
        self._render_items()
        for name in self._pinned_order:
            self.clients_cache.setdefault(name, [])

    def toggle_pinned(self, box: Box, action: Literal["show", "hide"]):
        hide = "dock-station-pinned-hide"
        show = "dock-station-pinned-show"
        ctx = box.get_style_context()

        if action == "show":
            ctx.remove_class(hide)
            ctx.add_class(show)
        elif action == "hide":
            ctx.remove_class(show)
            ctx.add_class(hide)

    def pinned_checker(self, app: str):
        if self._normalize(app) in self.pinned_list:
            return True
        return False

    def click_handler(
        self,
        widget: Gtk.Widget,
        event: Gdk.EventButton,
        inner_box: Box,
        overlay: Overlay,
        app: str,
        instances: list[dict],
    ):
        if event.button == 1:
            self.action.handle_app(app, instances)

        elif event.button == 3:
            self.toggle_pinned(inner_box, "show")

            pin_label = Label(
                label=self._cfg.pinned_icon
                if not self.pinned_checker(app)
                else self._cfg.unpinned_icon,
                name="dock-station-pin-indicator",
                size=self.icons_size,
            )
            overlay.add_overlay(pin_label)
            overlay.show_all()

            def remove_pin():
                overlay.remove(pin_label)
                self.toggle_pinned(inner_box, "hide")
                return False

            GLib.timeout_add(400, remove_pin)

            if self.pinned_checker(app):
                self.pinned_list.remove(self._normalize(app))
                self.json.update(DOCK_STATION_PINS, "pinned", self.pinned_list)
            else:
                self.pinned_list.append(self._normalize(app))
                self.json.update(DOCK_STATION_PINS, "pinned", self.pinned_list)

            GLib.timeout_add(800, self._cfg.dock.refresh_ui)
