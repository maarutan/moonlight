from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class NetworkSpeedCfg:
    def __init__(self, cfg_handler: "ConfigHandlerStatusBar") -> None:
        self._cfg = cfg_handler
        self.parent = "network-speed"

    def icons(self):
        dflt = {
            "download": "󰇚",
            "upload": "󰕒",
            "if_one": "",
            "position": "left",
        }
        i = self._cfg._get_nested(self.parent, "icons", default=dflt)
        return i if isinstance(i, dict) else dflt

    def interval(self) -> int:
        dflt = 1
        i = self._cfg._get_nested(self.parent, "interval", default=dflt)
        return i if isinstance(i, int) else dflt

    def speed_type(self) -> str:
        dflt = "download"
        s = self._cfg._get_nested(self.parent, "speed_type", default=dflt)
        return s if isinstance(s, str) and s in ("download", "upload", "all") else dflt
