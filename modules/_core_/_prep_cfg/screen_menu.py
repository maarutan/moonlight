from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


class ScreenMenuCfg:
    def __init__(self, cfg: "CoreConfigHandler"):
        self._cfg = cfg
        self.parent = "screen-menu"

    def enabled(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "enabled", default=dflt)
        return i if isinstance(i, bool) else dflt

    def list_items(self) -> list:
        dflt = [
            {
                "icon": "",
                "name": "Empty Item",
                "cmd": "notify-send 'Empty item'",
            }
        ]
        i = self._cfg._get_nested(self.parent, "items", default=dflt)
        return i if isinstance(i, list) else dflt
