from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class WindowsTitleCfg:
    def __init__(self, cfg_handler: "ConfigHandlerStatusBar") -> None:
        self._cfg = cfg_handler
        self.parent = "windows-title"

    def truncation(self) -> bool:
        dflt = False
        i = self._cfg._get_nested(self.parent, "truncate", default=dflt)
        return i if isinstance(i, bool) else dflt

    def truncation_size(self) -> int:
        dflt = 80
        i = self._cfg._get_nested(self.parent, "truncate-size", default=dflt)
        return i if isinstance(i, int) else dflt

    def map(self) -> list:
        dflt = []
        i = self._cfg._get_nested(self.parent, "map", default=dflt)
        return i if isinstance(i, list) else dflt

    def enable_icon(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "icon_enable", default=dflt)
        return i if isinstance(i, bool) else dflt

    def vertical_title_length(self) -> int:
        dflt = 6
        i = self._cfg._get_nested(self.parent, "vertical-length", default=dflt)
        return i if isinstance(i, int) else dflt

    def exceptions(self):
        dflt = []
        i = self._cfg._get_nested(self.parent, "exceptions", default=dflt)
        return i if isinstance(i, list) else dflt

    def icon_resolve(self) -> dict:
        dflt = {}
        i = self._cfg._get_nested(self.parent, "icon_resolve", default=dflt)
        return i if isinstance(i, dict) else dflt

    def title_type(self) -> dict:
        dflt = {}
        i = self._cfg._get_nested(self.parent, "title-type", default=dflt)
        return i if isinstance(i, dict) else dflt
