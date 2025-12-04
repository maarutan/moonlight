from typing import Optional, List
from pathlib import Path
import re

from fabric.utils.helpers import get_desktop_applications, DesktopApp
from fabric.widgets.image import Image
from fabric.widgets.box import Box

from gi.repository import GLib, Gtk, GdkPixbuf  # type: ignore

from utils.constants import Const


class AppIcon(Box):
    def __init__(
        self,
        app_name: str,
        include_hidden: bool = False,
        icon_size: int = 48,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.query = (app_name or "").strip()
        self.include_hidden = include_hidden
        self.icon_size = int(icon_size or 48)

        self.app: Optional[DesktopApp] = self._find_app()

        pixbuf = None

        if self.app:
            try:
                pixbuf = self.app.get_icon_pixbuf(self.icon_size)
            except Exception:
                pixbuf = None

        if pixbuf is None:
            candidates = []
            if self.app:
                if getattr(self.app, "icon_name", None):
                    candidates.append(self.app.icon_name)
                if getattr(self.app, "name", None):
                    candidates.append(self.app.name)
                if getattr(self.app, "generic_name", None):
                    candidates.append(self.app.generic_name)
            candidates.append(self.query)

            icon_name = None
            for cand in filter(None, candidates):
                icon_name = self._compositor_find_icon(str(cand))
                if icon_name:
                    pixbuf = self._load_icon_pixbuf(icon_name, self.icon_size)
                    if pixbuf:
                        break
                    icon_name = None

            if pixbuf is None:
                desktop_path = self._get_desktop_file(self.query)
                if desktop_path:
                    icon_from_desktop = self._get_icon_from_desktop_file(desktop_path)
                    if icon_from_desktop:
                        pixbuf = self._load_icon_pixbuf(
                            icon_from_desktop, self.icon_size
                        )

        if pixbuf is not None:
            self.children = Image(pixbuf=pixbuf)
        else:
            self.children = Image(
                image_file=Const.PLACEHOLDER_IMAGE_GHOST.as_posix(), size=self.icon_size
            )

        self.show_all()

    def _find_app(self) -> Optional[DesktopApp]:
        matches = self._find_app_by_partial_name(self.query, self.include_hidden)
        return matches[0] if matches else None

    def _find_app_by_partial_name(
        self, query: str, include_hidden: bool = False
    ) -> List[DesktopApp]:
        q = (query or "").casefold()
        found: List[DesktopApp] = []

        for app in get_desktop_applications(include_hidden):
            parts = [
                (app.name or ""),
                (app.display_name or ""),
                (getattr(app, "icon_name", "") or ""),
                (getattr(app, "generic_name", "") or ""),
                (getattr(app, "window_class", "") or ""),
                (getattr(app, "executable", "") or ""),
                (
                    getattr(app, "_app", None)
                    and getattr(app._app, "get_id", lambda: "")()
                ),  # try to get app id if available
            ]

            try:
                filename = getattr(app, "filename", None)
                if filename:
                    parts.append(str(filename))
            except Exception:
                pass

            for part in parts:
                if not part:
                    continue
                if q in str(part).casefold():
                    found.append(app)
                    break

        return found

    def _load_icon_pixbuf(
        self, icon_name: str, size: int
    ) -> Optional[GdkPixbuf.Pixbuf]:
        theme = Gtk.IconTheme.get_default()  # type: ignore
        if not icon_name:
            return None

        if Path(icon_name).is_file():
            try:
                return GdkPixbuf.Pixbuf.new_from_file_at_size(icon_name, size, size)
            except Exception:
                return None

        try:
            return theme.load_icon(icon_name, size, Gtk.IconLookupFlags.FORCE_SIZE)  # type: ignore
        except Exception:
            try:
                return theme.load_icon(
                    f"{icon_name}-desktop",
                    size,
                    Gtk.IconLookupFlags.FORCE_SIZE,  # type: ignore
                )
            except Exception:
                return None

    def _compositor_find_icon(self, app_id: str) -> str:
        if not app_id:
            return ""

        theme = Gtk.IconTheme.get_default()  # type: ignore
        cand = app_id

        try:
            if theme.has_icon(cand):
                return cand
        except Exception:
            pass

        try:
            if theme.has_icon(f"{cand}-desktop"):
                return f"{cand}-desktop"
        except Exception:
            pass

        desktop_file = self._get_desktop_file(app_id)
        if desktop_file:
            icon_name = self._get_icon_from_desktop_file(desktop_file)
            return icon_name or ""

        return ""

    def _get_icon_from_desktop_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Icon="):
                        return "".join(line.strip()[5:].split())
        except Exception:
            pass
        return ""

    def _get_desktop_file(self, app_id: str) -> Optional[str]:
        search_dirs = [Path(GLib.get_user_data_dir()) / "applications"]
        search_dirs += [Path(d) / "applications" for d in GLib.get_system_data_dirs()]

        for dir_path in search_dirs:
            if not dir_path.exists():
                continue
            try:
                files = list(dir_path.iterdir())
            except Exception:
                continue

            match = [f for f in files if app_id.lower() in f.name.lower()]
            if match:
                return str(match[0])

            parts = re.split(r"[-_.\s]", app_id)
            for word in filter(None, parts):
                match = [f for f in files if word.lower() in f.name.lower()]
                if match:
                    return str(match[0])

        return None
