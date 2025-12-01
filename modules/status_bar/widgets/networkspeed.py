from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.eventbox import EventBox
from fabric.utils.helpers import idle_add, GLib
from services.networkspeed import NetworkSpeedService
from utils.widget_utils import setup_cursor_hover, merge
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..bar import StatusBar


class NetworkSpeedWidget(Box):
    def __init__(self, init_class: "StatusBar"):
        self.conf = init_class

        super().__init__(
            name="sb_network-speed",
            v_expand=True,
            h_expand=True,
            v_align="center",
            h_align="center",
        )
        setup_cursor_hover(self)

        if self.conf.is_horizontal():
            self.add_style_class("sb_network-speed-horizontal")
        else:
            self.add_style_class("sb_network-speed-vertical")

        self.nws = NetworkSpeedService()
        self.label = Label("")

        self.inner = EventBox(
            child=Box(
                name="sb_network-speed-inner",
                children=[self.label],
                h_align="center",
                v_align="center",
            )
        )
        self.children = self.inner

        config = (
            self.conf.confh.get_option(f"{self.conf.widget_name}.widgets.network-speed")
            or {}
        )

        self.conf_status = config.get("status", {}) or {}
        self.conf_delim_icon = self.conf_status.get("delim-icon", "")
        self.conf_download = self.conf_status.get("download", {}) or {}
        self.conf_upload = self.conf_status.get("upload", {}) or {}

        self.conf_if_vertical = config.get("if-vertical", {}) or {}

        self._original_show_state: Dict[str, bool] = {
            "download": bool(self.conf_download.get("show", True)),
            "upload": bool(self.conf_upload.get("show", True)),
        }

        self._temp_show_state: Dict[str, bool] = dict(self._original_show_state)

        self._mode = "original"

        idle_add(self.update)
        GLib.timeout_add(1000, self.update)

    def build_text(
        self,
        speeds: dict,
        conf_download: dict,
        conf_upload: dict,
        is_vertical: bool,
        delim: str,
    ) -> str:
        parts = []
        download_show = self._temp_show_state.get(
            "download", True
        ) and conf_download.get("show", True)
        upload_show = self._temp_show_state.get("upload", True) and conf_upload.get(
            "show", True
        )
        if download_show:
            icon = conf_download.get("icon", "")
            speed = speeds.get("download", "")
            if is_vertical:
                if icon:
                    parts.append(f" {icon}\n{speed}")
                else:
                    parts.append(f"{speed}")
            else:
                parts.append(f"{icon} {speed}".strip())
        if download_show and upload_show and delim:
            parts.append(delim)
        if upload_show:
            icon = conf_upload.get("icon", "")
            speed = speeds.get("upload", "")
            if is_vertical:
                if icon:
                    parts.append(f" {icon}\n{speed}")
                else:
                    parts.append(f"{speed}")
            else:
                parts.append(f"{icon} {speed}".strip())
        if not parts:
            return ""
        return "\n".join(parts) if is_vertical else " ".join(parts).strip()

    def update(self):
        nws_dict = self.nws.get_network_speed()
        is_horizontal = self.conf.is_horizontal()
        is_vertical = not is_horizontal
        conf_download_local = self.conf_download
        conf_upload_local = self.conf_upload
        conf_delim_local = self.conf_delim_icon
        if is_vertical and self.conf_if_vertical:
            iv = self.conf_if_vertical
            if "status" in iv and isinstance(iv.get("status"), dict):
                vs = iv["status"]
                conf_download_local = merge(conf_download_local, vs.get("download", {}))
                conf_upload_local = merge(conf_upload_local, vs.get("upload", {}))
                conf_delim_local = vs.get("delim-icon", conf_delim_local)
            else:
                conf_download_local = merge(conf_download_local, iv.get("download", {}))
                conf_upload_local = merge(conf_upload_local, iv.get("upload", {}))
                conf_delim_local = iv.get("delim-icon", conf_delim_local)
        speeds = nws_dict["horizontal"] if is_horizontal else nws_dict["vertical"]
        text = self.build_text(
            speeds,
            conf_download_local,
            conf_upload_local,
            is_vertical,
            conf_delim_local,
        )
        self.label.set_text(text)
        return True
