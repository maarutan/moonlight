from typing import TYPE_CHECKING

from config.data import PLACEHOLDER_IMAGE

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class ProfileCfg:
    def __init__(self, cfg_handler: "ConfigHandlerStatusBar") -> None:
        self._cfg = cfg_handler
        self.parent = "profile"

    def logo(self) -> dict:
        dflt = {
            "type": "text",
            "content": "logo",
            "image-path": PLACEHOLDER_IMAGE,
            "image-size": 24,
        }
        i = self._cfg._get_nested(self.parent, "logo", default=dflt)
        return i if isinstance(i, dict) else dflt

    def dashboard_profile_preview(self) -> dict:
        dflt = {
            "username": "sex mashina",
            "image": {
                "shape": "circle",
                "path": PLACEHOLDER_IMAGE.as_posix(),
                "size": 38,
            },
            "uptime": {
                "enable": True,
                "format": "hours:%H minutes:%M",
            },
        }
        i = self._cfg._get_nested(
            self.parent, "dashboard-profile-preview", default=dflt
        )
        return i if isinstance(i, dict) else dflt
