import re
from typing import Optional
from loguru import logger
from utils import JsonManager
from pathlib import Path
import gi
from gi.repository import GLib, Gtk, GdkPixbuf, Gio  # type: ignore

gi.require_version("Gtk", "3.0")


class IconResolver:
    def __init__(
        self,
        icon_lock: Path,
        default_icon="application-x-executable-symbolic",
    ):
        self.icon_lock = icon_lock
        self.json = JsonManager()
        self.default_icon = default_icon
        self._icon_dict = {}

        if icon_lock.exists():
            self._icon_dict = self.json.get_data(icon_lock)

    def get_icon_name(self, app_id: str) -> str:
        if app_id in self._icon_dict:
            return self._icon_dict[app_id]

        new_icon = self._compositor_find_icon(app_id)
        logger.info(
            f"[ICONS] found new icon: '{new_icon}' for app id: '{app_id}', storing..."
        )
        self._store_new_icon(app_id, new_icon)
        return new_icon

    def get_icon_pixbuf(
        self, app_id: str, size: int = 16
    ) -> Optional[GdkPixbuf.Pixbuf]:
        try:
            return Gtk.IconTheme.get_default().load_icon(
                self.get_icon_name(app_id),
                size,
                Gtk.IconLookupFlags.FORCE_SIZE,
            )
        except Exception:
            try:
                return Gtk.IconTheme.get_default().load_icon(
                    self.default_icon, size, Gtk.IconLookupFlags.FORCE_SIZE
                )
            except Exception:
                return None

    def _store_new_icon(self, app_id: str, icon: str) -> None:
        self._icon_dict[app_id] = icon
        self.json.write(self.icon_lock, self._icon_dict, indent=2)

    def _get_icon_from_desktop_file(self, path: str):
        try:
            with open(path) as f:
                for line in f:
                    if line.startswith("Icon="):
                        return "".join(line.strip()[5:].split())
        except Exception:
            pass
        return self.default_icon

    def _get_desktop_file(self, app_id: str) -> Optional[str]:
        search_dirs = [Path(GLib.get_user_data_dir()) / "applications"]
        search_dirs += [Path(d) / "applications" for d in GLib.get_system_data_dirs()]

        for dir_path in search_dirs:
            if not dir_path.exists():
                continue

            files = list(dir_path.iterdir())

            match = [f for f in files if app_id.lower() in f.name.lower()]
            if match:
                return str(match[0])

            parts = re.split(r"[-_.\s]", app_id)
            for word in filter(None, parts):
                match = [f for f in files if word.lower() in f.name.lower()]
                if match:
                    return str(match[0])

    def _compositor_find_icon(self, app_id: str) -> str:
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

    def get_icon_from_appinfo(self, appinfo: Gio.AppInfo, size: int = 16):
        try:
            icon = appinfo.get_icon()
            if icon:
                return Gtk.IconTheme.get_default().load_icon(
                    icon.to_string(), size, Gtk.IconLookupFlags.FORCE_SIZE
                )
        except Exception:
            pass
        return None
