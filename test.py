from datetime import timedelta
from typing import Literal, Optional
from pathlib import Path
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.image import Image

from config.data import PLACEHOLDER_IMAGE
from widgets import CircleImage
from utils import FileManager

import gi
from gi.repository import Gtk  # type:ignore

gi.require_version("Gtk", "3.0")


class ProfilePreview(Box):
    def __init__(
        self,
        username: str = "Anonymous",
        uptime: Optional[dict] = None,
        image: Optional[dict] = None,
    ) -> None:
        self._uptime = uptime or {
            "enable": False,
            "format": "%H:%M:%S",
        }
        self._image = image or {
            "shape": "circle",
            "path": str(PLACEHOLDER_IMAGE),
            "size": 24,
        }
        self._username = username

        self._image_path = self._image.get("path", str(PLACEHOLDER_IMAGE))
        self._image_size = self._image.get("size", 24)
        self._image_shape = self._image.get("shape", "circle")
        self.fm = FileManager()
        print(self.__get_uptime())

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
        path = Path(self._image_path).expanduser()
        if not path.exists():
            path = Path(str(PLACEHOLDER_IMAGE))

        widget_class = CircleImage if self._image_shape == "circle" else Image
        return widget_class(
            name="statusbar-profile-dashboard-profile-preview-image-child",
            h_align="center",
            image_file=str(path),
            size=self._image_size,
        )

    def _make_profile_info(self) -> Box:
        return Box()  # заглушка

    def __get_uptime(self) -> str | None:
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


p = ProfilePreview(
    username="maaru",
    uptime={
        "enable": True,
        # "format":"%H:%M:%S"
        "format": "hours: %H minutes: %M seconds: %S",
    },
)
