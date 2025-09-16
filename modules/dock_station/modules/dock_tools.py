from typing import TYPE_CHECKING, Literal
from fabric.widgets.button import Button
from gi.repository import GLib  # type: ignore
from fabric.utils.helpers import idle_add

from modules.dock_station.modules.items import Items
from utils.widget_utils import setup_cursor_hover  # type: ignore

if TYPE_CHECKING:
    from ..dock import Dock


class DockTools:
    def __init__(self, cfg: "Dock"):
        self._cfg = cfg
        self.dock_position = self._cfg._anchor_handler()

    def cancel_hide(self):
        if self._cfg.hide_id:
            GLib.source_remove(self._cfg.hide_id)
            self._cfg.hide_id = None

    def toggle(self, action: Literal["show", "hide"]):
        ctx = self._cfg.content.get_style_context()
        if action == "show" and self._cfg.is_dock_hide:
            self._cfg.is_dock_hide = False
            ctx.add_class("dock-station-show")
            ctx.remove_class("dock-station-hide")

        elif action == "hide" and not self._cfg.is_dock_hide:
            self._cfg.is_dock_hide = True
            ctx.add_class("dock-station-hide")
            ctx.remove_class("dock-station-show")

    def _on_hover_enter(self, *_):
        self.cancel_hide()
        self.toggle("show")

    def _on_wrapper_enter(self, *_):
        self.cancel_hide()

    def _on_wrapper_leave(self, *_):
        self.auto_hide_check()

    def delay_hide(self):
        self.cancel_hide()
        self.toggle("hide")

    def hide_dock(self):
        self.toggle("hide")
        self._cfg.hide_id = None
        return False

    def auto_hide_check(self, *_):
        clients = list(self._cfg.clients_cache.values())
        ws = self._cfg.current_ws
        ws_clients = [w for w in clients if w["workspace"]["id"] == ws]

        if not ws_clients:
            self.toggle("show")
            return

        try:
            monitors = self._cfg.json.loads(
                self._cfg.conn.send_command("j/monitors").reply.decode()
            )
            focused = next((m for m in monitors if m.get("focused")), None)
            if not focused:
                self.toggle("show")
                return
            monitor_height = focused["height"]
            monitor_width = focused["width"]
        except Exception:
            self.toggle("show")
            return

        if self.dock_position == "bottom":
            dock_x1, dock_x2 = 0, monitor_width
            dock_y1, dock_y2 = monitor_height - self._cfg.dock_size, monitor_height
        elif self.dock_position == "top":
            dock_x1, dock_x2 = 0, monitor_width
            dock_y1, dock_y2 = 0, self._cfg.dock_size
        elif self.dock_position == "left":
            dock_x1, dock_x2 = 0, self._cfg.dock_size
            dock_y1, dock_y2 = 0, monitor_height
        elif self.dock_position == "right":
            dock_x1, dock_x2 = monitor_width - self._cfg.dock_size, monitor_width
            dock_y1, dock_y2 = 0, monitor_height
        else:
            self.toggle("show")
            return

        for window in ws_clients:
            if window.get("fullscreen"):
                continue
            pos_x, pos_y = window["at"]
            size_x, size_y = window["size"]

            win_left, win_right = pos_x, pos_x + size_x
            win_top, win_bottom = pos_y, pos_y + size_y

            intersects_x = not (win_right <= dock_x1 or win_left >= dock_x2)
            intersects_y = not (win_bottom <= dock_y1 or win_top >= dock_y2)

            if intersects_x and intersects_y:
                self.delay_hide()
                return

        self.toggle("show")

    def _init_subscriptions(self, *_):
        for ev in (
            "activewindow",
            "openwindow",
            "closewindow",
            "changefloatingmode",
            "move",
        ):
            self._cfg.conn.connect(f"event::{ev}", self._on_event)
        self._cfg.conn.connect("event::workspace", self._on_event)
        self._cfg._update_state()
        self.auto_hide_check()

    def _on_event(self, *_):
        self._cfg._update_state()
        self.auto_hide_check()

    def refresh_ui(self):
        self.cancel_hide()
        self.toggle("hide")

        def refresh() -> bool:
            self._cfg._update_state()

            for child in list(self._cfg.view.get_children()):
                self._cfg.view.remove(child)

            self._cfg.items = Items(self._cfg)
            setup_cursor_hover(self._cfg.items)
            if self._cfg.menu_position == "left":
                if getattr(self._cfg, "result_menu", None):
                    self._cfg.view.add(self._cfg.result_menu)
                self._cfg.view.add(self._cfg.items)
            else:
                self._cfg.view.add(self._cfg.items)
                if getattr(self._cfg, "result_menu", None):
                    self._cfg.view.add(self._cfg.result_menu)

            self._cfg.view.show_all()
            self.auto_hide_check()
            return False

        idle_add(refresh)
