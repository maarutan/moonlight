from typing import Optional, List, Dict, Tuple
from pathlib import Path
import re

from fabric.utils.helpers import get_desktop_applications, DesktopApp
from fabric.widgets.image import Image
from fabric.widgets.box import Box

from gi.repository import GLib, Gtk, GdkPixbuf  # type: ignore

from utils.constants import Const


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").casefold())


def _token_set(s: str) -> set:
    return set(p for p in re.split(r"[^a-z0-9]+", (s or "").casefold()) if p)


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
                ),
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

        simple = _normalize(cand)
        try:
            if simple and theme.has_icon(simple):
                return simple
        except Exception:
            pass

        parts = re.split(r"[^a-z0-9]+", cand.casefold())
        for p in parts:
            if not p:
                continue
            try:
                if theme.has_icon(p):
                    return p
            except Exception:
                continue
            try:
                if theme.has_icon(f"{p}-desktop"):
                    return f"{p}-desktop"
            except Exception:
                continue

        desktop_file = self._get_desktop_file(app_id)
        if desktop_file:
            info = self._parse_desktop_file(desktop_file)
            icon_from_desktop = info.get("Icon")
            if icon_from_desktop:
                return icon_from_desktop
            wm = info.get("StartupWMClass")
            if wm:
                try:
                    if theme.has_icon(wm):
                        return wm
                except Exception:
                    pass
                simple_wm = _normalize(wm)
                try:
                    if simple_wm and theme.has_icon(simple_wm):
                        return simple_wm
                except Exception:
                    pass

        return ""

    def _parse_desktop_file(self, path: str) -> Dict[str, str]:
        data: Dict[str, str] = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                in_entry = False
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("["):
                        in_entry = line.lower().startswith("[desktop entry")
                        continue
                    if not in_entry:
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        data[k.strip()] = v.strip()
        except Exception:
            pass
        return data

    def _get_icon_from_desktop_file(self, path: str) -> str:
        parsed = self._parse_desktop_file(path)
        icon = parsed.get("Icon", "")
        return "".join(icon.split()) if icon else ""

    def _score_desktop_file(self, query: str, parsed: Dict[str, str]) -> float:
        """Return a score [0..1] how well parsed .desktop matches query."""
        if not query:
            return 0.0

        q_norm = _normalize(query)
        q_tokens = _token_set(query)

        # prefer StartupWMClass exact or near match
        wm = parsed.get("StartupWMClass", "")
        if wm:
            wm_norm = _normalize(wm)
            if wm_norm and (
                wm_norm == q_norm or wm_norm in q_norm or q_norm in wm_norm
            ):
                return 1.0
            wm_tokens = _token_set(wm)
            inter = q_tokens.intersection(wm_tokens)
            if inter:
                return 0.9

        # prefer exact name match
        name = parsed.get("Name", "")
        if name:
            name_norm = _normalize(name)
            if name_norm and (
                name_norm == q_norm or name_norm in q_norm or q_norm in name_norm
            ):
                return 0.95

        # Exec match by binary name
        exec_line = parsed.get("Exec", "")
        if exec_line:
            exec_bin = exec_line.split()[0]
            exec_base = Path(exec_bin).name
            if _normalize(exec_base) and (
                _normalize(exec_base) == q_norm
                or _normalize(exec_base) in q_norm
                or q_norm in _normalize(exec_base)
            ):
                return 0.93

        # token overlap on Name/Icon/Keywords
        fields = " ".join(
            parsed.get(k, "")
            for k in ("Name", "GenericName", "Keywords", "Comment", "Icon")
        )
        f_tokens = _token_set(fields)
        if not f_tokens:
            return 0.0
        inter = q_tokens.intersection(f_tokens)
        score = len(inter) / max(len(q_tokens.union(f_tokens)), 1)
        return float(score) * 0.8  # scale down

    def _get_desktop_file(self, app_id: str) -> Optional[str]:
        search_dirs = [Path(GLib.get_user_data_dir()) / "applications"]
        search_dirs += [Path(d) / "applications" for d in GLib.get_system_data_dirs()]

        query = (app_id or "").strip()
        if not query:
            return None

        candidates: List[Path] = []
        for dir_path in search_dirs:
            if not dir_path.exists():
                continue
            try:
                for f in dir_path.iterdir():
                    if f.is_file():
                        candidates.append(f)
            except Exception:
                continue

        best_score = 0.0
        best_path: Optional[Path] = None

        # parse each desktop file once and score
        for f in candidates:
            try:
                parsed = self._parse_desktop_file(str(f))
            except Exception:
                parsed = {}
            score = self._score_desktop_file(query, parsed)
            if score > best_score:
                best_score = score
                best_path = f

        # accept if score reasonable
        if best_score >= 0.25 and best_path:
            return str(best_path)

        # fallback to filename partial match (old behaviour)
        q_lower = query.casefold()
        for f in candidates:
            name_no_ext = f.stem.casefold()
            if q_lower in name_no_ext:
                return str(f)

        return None
