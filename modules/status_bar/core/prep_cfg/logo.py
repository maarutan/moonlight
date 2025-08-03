from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandler


class LogoCfg:
    def __init__(self, cfg_handler: "ConfigHandler") -> None:
        self._cfg = cfg_handler
        self.parent = "logo"

    def type(self) -> str:
        dflt = "text"
        i = self._cfg._get_nested(self.parent, "type", default=dflt)
        return i if isinstance(i, str) else dflt

    def content(self) -> str:
        dflt = "logo"
        i = self._cfg._get_nested(self.parent, "content", default=dflt)
        return i if isinstance(i, str) else dflt

    def image_path(self) -> str:
        dflt = ""
        i = self._cfg._get_nested(self.parent, "image-path", default=dflt)
        return i if isinstance(i, str) else dflt

    def image_size(self) -> int:
        dflt = 24
        i = self._cfg._get_nested(self.parent, "image-size", default=dflt)
        return i if isinstance(i, int) else dflt
