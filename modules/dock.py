import json
import os
import re
import threading
from gi.repository import GLib, Gtk, GdkPixbuf
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.eventbox import EventBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import get_hyprland_connection
from fabric.utils import exec_shell_command, idle_add, remove_handler
from loguru import logger

# === IconResolver ===

CACHE_DIR = str(GLib.get_user_cache_dir()) + "/modus"
ICON_CACHE_FILE = os.path.join(CACHE_DIR, "icons.json")
os.makedirs(CACHE_DIR, exist_ok=True)


class IconResolver:
    def __init__(self, default_icon="application-x-executable-symbolic"):
        self.default_icon = default_icon
        self._icon_dict = {}

        if os.path.exists(ICON_CACHE_FILE):
            try:
                with open(ICON_CACHE_FILE) as f:
                    self._icon_dict = json.load(f)
            except json.JSONDecodeError:
                logger.info("[ICONS] Cache file is corrupted")

    def get_icon_name(self, app_id: str):
        if app_id in self._icon_dict:
            return self._icon_dict[app_id]

        new_icon = self._compositor_find_icon(app_id)
        logger.info(
            f"[ICONS] found new icon: '{new_icon}' for app id: '{app_id}', storing..."
        )
        self._store_new_icon(app_id, new_icon)
        return new_icon

    def get_icon_pixbuf(self, app_id: str, size: int = 16):
        try:
            return Gtk.IconTheme.get_default().load_icon(
                self.get_icon_name(app_id),
                size,
                Gtk.IconLookupFlags.FORCE_SIZE,
            )
        except Exception:
            return None

    def _store_new_icon(self, app_id: str, icon: str):
        self._icon_dict[app_id] = icon
        with open(ICON_CACHE_FILE, "w") as f:
            json.dump(self._icon_dict, f)

    def _get_icon_from_desktop_file(self, path: str):
        try:
            with open(path) as f:
                for line in f:
                    if line.startswith("Icon="):
                        return "".join(line.strip()[5:].split())
        except Exception:
            pass
        return self.default_icon

    def _get_desktop_file(self, app_id: str):
        for data_dir in GLib.get_system_data_dirs():
            dir_path = os.path.join(data_dir, "applications")
            if not os.path.exists(dir_path):
                continue

            files = os.listdir(dir_path)
            match = [f for f in files if app_id.lower() in f.lower()]
            if match:
                return os.path.join(dir_path, match[0])

            parts = re.split(r"[-_.\s]", app_id)
            for word in filter(None, parts):
                match = [f for f in files if word.lower() in f.lower()]
                if match:
                    return os.path.join(dir_path, match[0])
        return None

    def _compositor_find_icon(self, app_id: str):
        theme = Gtk.IconTheme.get_default()
        if theme.has_icon(app_id):
            return app_id
        if theme.has_icon(app_id + "-desktop"):
            return app_id + "-desktop"
        desktop_file = self._get_desktop_file(app_id)
        return (
            self._get_icon_from_desktop_file(desktop_file)
            if desktop_file
            else self.default_icon
        )


# === Dock ===


class Dock(Window):
    def __init__(self, **kwargs):
        super().__init__(
            layer="top", anchor="bottom center", exclusivity="none", **kwargs
        )
        self.config = {"pinned_apps": []}
        self.conn = get_hyprland_connection()
        self.icon = IconResolver()
        self.pinned = self.config["pinned_apps"]
        self.is_hidden = False
        self.hide_id = None
        self._arranger_handler = None

        self.view = Box(name="viewport", orientation="h")
        self.wrapper = Box(name="dock", orientation="v", children=[self.view])
        self.hover = EventBox()
        self.hover.set_size_request(-1, 1)
        self.hover.connect("enter-notify-event", self._on_hover_enter)
        self.hover.connect("leave-notify-event", self._on_hover_leave)
        self.view.connect("enter-notify-event", self._on_hover_enter)
        self.view.connect("leave-notify-event", self._on_hover_leave)
        self.main_box = Box(orientation="v", children=[self.wrapper, self.hover])
        self.add(self.main_box)

        if self.conn.ready:
            self.update_dock()
            GLib.timeout_add(500, self.check_hide)
        else:
            self.conn.connect("event::ready", self.update_dock)
            self.conn.connect("event::ready", self.check_hide)

        for ev in ("activewindow", "openwindow", "closewindow", "changefloatingmode"):
            self.conn.connect(f"event::{ev}", self.update_dock)
        self.conn.connect("event::workspace", self.check_hide)

    def _on_hover_enter(self, *_):
        self.toggle_dock(True)

    def _on_hover_leave(self, *_):
        self.delay_hide()

    def toggle_dock(self, show: bool):
        if show and self.is_hidden:
            self.is_hidden = False
            self.wrapper.add_style_class("show-dock")
            self.wrapper.remove_style_class("hide-dock")
            if self.hide_id:
                GLib.source_remove(self.hide_id)
                self.hide_id = None
        elif not show and not self.is_hidden:
            self.is_hidden = True
            self.wrapper.add_style_class("hide-dock")
            self.wrapper.remove_style_class("show-dock")

    def delay_hide(self):
        if self.hide_id:
            GLib.source_remove(self.hide_id)
        self.hide_id = GLib.timeout_add(1000, self.hide_dock)

    def hide_dock(self):
        self.toggle_dock(False)
        self.hide_id = None
        return False

    def check_hide(self, *_):
        clients = self.get_clients()
        ws = self.get_workspace()
        ws_clients = [w for w in clients if w["workspace"]["id"] == ws]
        if not ws_clients:
            self.toggle_dock(True)
        elif any(not w.get("floating") and not w.get("fullscreen") for w in ws_clients):
            self.delay_hide()
        else:
            self.toggle_dock(True)

    def update_dock(self, *_):
        if self._arranger_handler:
            remove_handler(self._arranger_handler)

        clients = self.get_clients()
        running = {}
        for c in clients:
            key = c["initialClass"].lower()
            running.setdefault(key, []).append(c)

        pinned_buttons = [
            self.create_button(app, running.get(app.lower(), [])) for app in self.pinned
        ]
        open_buttons = [
            self.create_button(
                c["initialClass"], running.get(c["initialClass"].lower(), [])
            )
            for group in running.values()
            for c in group
            if c["initialClass"].lower() not in self.pinned
        ]

        children = pinned_buttons
        if pinned_buttons and open_buttons:
            children += [Box(orientation="v", v_expand=True, name="dock-separator")]
        children += open_buttons
        self.view.children = children
        idle_add(self._update_size)

    def _update_size(self):
        width, _ = self.view.get_preferred_width()
        self.set_size_request(width, -1)
        return False

    def create_button(self, app, instances):
        icon = self.icon.get_icon_pixbuf(app.lower(), 30) or self.icon.get_icon_pixbuf(
            "image-missing", 30
        )
        items = [Image(pixbuf=icon)]
        if instances:
            items.append(
                Image(
                    pixbuf=self.icon.get_icon_pixbuf("find-location-symbolic", 11),
                    name="dock-app-indicator",
                )
            )
        return Button(
            child=Box(
                name="dock-icon", orientation="v", h_align="center", children=items
            ),
            on_clicked=lambda *a: self.handle_app(app, instances),
            tooltip_text=instances[0]["title"] if instances else app,
            name="dock-app-button",
        )

    def handle_app(self, app, instances):
        if not instances:
            threading.Thread(
                target=exec_shell_command, args=(f"nohup {app}",), daemon=True
            ).start()
        else:
            focused = self.get_focused()
            idx = next(
                (i for i, inst in enumerate(instances) if inst["address"] == focused),
                -1,
            )
            next_inst = instances[(idx + 1) % len(instances)]
            exec_shell_command(
                f"hyprctl dispatch focuswindow address:{next_inst['address']}"
            )

    def get_clients(self):
        try:
            return json.loads(self.conn.send_command("j/clients").reply.decode())
        except json.JSONDecodeError:
            return []

    def get_focused(self):
        try:
            return json.loads(
                self.conn.send_command("j/activewindow").reply.decode()
            ).get("address", "")
        except json.JSONDecodeError:
            return ""

    def get_workspace(self):
        try:
            return json.loads(
                self.conn.send_command("j/activeworkspace").reply.decode()
            ).get("id", 0)
        except json.JSONDecodeError:
            return 0
