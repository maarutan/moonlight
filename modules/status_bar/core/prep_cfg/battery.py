from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class BatteryCfg:
    def __init__(self, cfg_handler: "ConfigHandlerStatusBar") -> None:
        self._cfg = cfg_handler
        self.parent = "battery"

    def percentage(self) -> dict:
        dflt = {}
        i = self._cfg._get_nested(self.parent, "percentage", default=dflt)
        if isinstance(i, dict):
            return i
        return dflt

    def icons(self) -> dict:
        dflt = {}
        i = self._cfg._get_nested(self.parent, "icons", default=dflt)
        if isinstance(i, dict):
            return i
        return dflt
