import requests
from pathlib import Path
from datetime import timedelta
from typing import Optional
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from config.data import PLACEHOLDER_IMAGE, URL_AVATAR
from utils import GetPreviewPath
from widgets import CircleImage
from utils import FileManager
import gi
from gi.repository import Gtk  # type: ignore

gi.require_version("Gtk", "3.0")


class ProfilePreview(Box):
    CACHE_IMAGE_PATH = Path.home() / ".cache" / "profile_preview_image.png"

    def __init__(
        self,
        name="statusbar-profile-dashboard-popup",
        profile_preview: Optional[dict] = None,
    ) -> None:
        self.get_preview = GetPreviewPath()
        self._dpp = profile_preview or {
            "username": "Anonymous",
            "image": {
                "path": PLACEHOLDER_IMAGE,
                "size": 130,
                "shape": "circle",
            },
            "uptime": {
                "enable": False,
                "format": "%H:%M:%S",
            },
        }

        self._uptime = self._dpp.get("uptime", {}) or {
            "enable": False,
            "format": "%H:%M:%S",
        }
        self._image = self._dpp.get("image", {}) or {
            "shape": "circle",
            "path": PLACEHOLDER_IMAGE,
            "size": 130,
        }

        self._username = self._dpp.get("username", "Anonymous")

        self._image_path = self._image.get("path", PLACEHOLDER_IMAGE)
        self._image_size = self._image.get("size", 130)
        self._image_shape = self._image.get("shape", "circle")
        self.fm = FileManager()

        super().__init__(
            name="statusbar-profile-dashboard-preview",
            h_align="start",
            orientation=Gtk.Orientation.HORIZONTAL,
            children=CenterBox(
                start_children=self._make_profile_image_preview(),
                end_children=self._make_profile_info(),
            ),
        )

    def _make_profile_image_preview(self) -> CircleImage | Image:
        path = self.get_cached_image_path(str(self._image_path))

        widget_class = CircleImage if self._image_shape == "circle" else Image
        return widget_class(
            name="statusbar-profile-dashboard-profile-preview-image-child",
            h_align="center",
            image_file=str(path),
            size=self._image_size,
        )

    def get_cached_image_path(self, path: str) -> Path:
        p = Path(path).expanduser()

        if p.exists():
            return p

        if path.startswith(("http://", "https://")) and self.get_preview.is_image_url(
            path
        ):
            return self.get_preview.download_and_cache_image(
                url=path, result=URL_AVATAR
            )

        return Path(str(PLACEHOLDER_IMAGE))

    def _make_profile_info(self) -> Box:
        return Box(
            name="statusbar-profile-dashboard-profile-preview-info-child",
            h_align="start",
            orientation=Gtk.Orientation.HORIZONTAL,
            children=[
                Label(
                    label=self._username,
                    name="statusbar-profile-dashboard-profile-preview-username-child",
                    h_align="start",
                ),
                Label(
                    label=self.__get_uptime() or "",
                    name="statusbar-profile-dashboard-profile-preview-uptime-child",
                    h_align="start",
                ),
            ],
        )

    def __get_uptime(self) -> Optional[str]:
        if not isinstance(self._uptime, dict):
            return None

        is_enable = self._uptime.get("enable", False)
        fmt = self._uptime.get("format", "%H:%M:%S")

        if not is_enable:
            return None

        try:
            f = self.fm.read(Path("/proc/uptime"))
            uptime_seconds = float(f.split()[0])
        except Exception:
            return None

        td = timedelta(seconds=int(uptime_seconds))
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        uptime_str = (
            fmt.replace("%H", f"{hours:02d}")
            .replace("%M", f"{minutes:02d}")
            .replace("%S", f"{seconds:02d}")
        )
        return uptime_str
