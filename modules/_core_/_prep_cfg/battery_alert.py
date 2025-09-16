from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


class BatteryAlertCfg:
    def __init__(self, cfg: "CoreConfigHandler"):
        self._cfg = cfg
        self.parent = "battery-alert"

    def enabled(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "enabled", default=dflt)
        return i if isinstance(i, bool) else dflt

    def icons(self) -> dict:
        dflt = {
            "low": "⚠",
            "medium": "⚠",
            "high": "!",
            "charging": "󱐋",
        }
        i = self._cfg._get_nested(self.parent, "icons", default=dflt)
        return i if isinstance(i, dict) else dflt

    def alert_progress(self) -> dict:
        dflt = {
            "low": 5,
            "medium": 20,
            "high": 80,
        }
        i = self._cfg._get_nested(self.parent, "alert_progress", default=dflt)
        return i if isinstance(i, dict) else dflt

    def hide_timeout(self) -> int:
        dflt = 3
        i = self._cfg._get_nested(self.parent, "hide_timeout", default=dflt)
        return i if isinstance(i, int) else dflt
