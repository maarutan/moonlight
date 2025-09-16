from typing import TYPE_CHECKING
from config import DOCK_MENU_ICON

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerDockStation


class DockCfg:
    def __init__(self, _cfg: "ConfigHandlerDockStation"):
        self._cfg = _cfg
        self.parent = "dock-station"

    def anchor(self) -> str:
        dflt = "bottom center"
        i = self._cfg._get_nested(self.parent, "anchor", default=dflt)
        if isinstance(i, str):
            return i
        return i

    def menu(self) -> dict:
        dflt = {
            "icon": "󰍜",
            "type": "hamburger",
            "position": "left",
            "path": DOCK_MENU_ICON,
        }
        i = self._cfg._get_nested(self.parent, "menu", default=dflt)
        if isinstance(i, dict):
            return i
        return dflt

    def size(self) -> int:
        dflt = 60
        i = self._cfg._get_nested(self.parent, "dock_size", default=dflt)
        if isinstance(i, int):
            return i
        return dflt

    def instance(self) -> dict:
        dflt = {
            "enabled": True,
            "max_items": 4,
            "icon": "•",
        }
        i = self._cfg._get_nested(self.parent, "instance", default=dflt)
        if isinstance(i, dict):
            return i
        return dflt

    def pinned(self) -> dict:
        dlft = {
            "pinned": "󰐃",
            "unpinned": "",
        }
        i = self._cfg._get_nested(self.parent, "pinned", default=dlft)
        if isinstance(i, dict):
            return i
        return dlft
