from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandler


class ScreenRecorderCfg:
    def __init__(self, cfg_handler: "ConfigHandler") -> None:
        self._cfg = cfg_handler
        self.parent = "screen-recorder"

    def icons(self) -> dict:
        dflt = {}
        i = self._cfg._get_nested(self.parent, "icons", default=dflt)
        return i if isinstance(i, dict) else dflt

    def blink(self) -> dict:
        dflt = {}
        i = self._cfg._get_nested(self.parent, "blink", default=dflt)
        return i if isinstance(i, dict) else dflt

    def timer(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "timer", default=dflt)
        return i if isinstance(i, bool) else dflt
