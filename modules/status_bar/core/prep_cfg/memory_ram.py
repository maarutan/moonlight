from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandler


class MemoryRamCfg:
    def __init__(self, cfg_handler: "ConfigHandler") -> None:
        self._cfg = cfg_handler
        self.parent = "memory_ram"

    def format(self) -> str:
        dflt = "used"
        i = self._cfg._get_nested(self.parent, "format", default=dflt)
        return i if isinstance(i, str) else dflt

    def interval(self) -> int:
        dflt = 1
        i = self._cfg._get_nested(self.parent, "interval", default=dflt)
        return i if isinstance(i, int) else dflt

    def icon(self) -> str:
        dflt = ""
        i = self._cfg._get_nested(self.parent, "icon", default=dflt)
        return i if isinstance(i, str) else dflt
