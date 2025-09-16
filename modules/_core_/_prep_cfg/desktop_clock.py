from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


class DesktopClockCfg:
    def __init__(self, cfg: "CoreConfigHandler"):
        self._cfg = cfg
        self.parent = "desktop-clock"

    def enabled(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "enabled", default=dflt)
        return i if isinstance(i, bool) else dflt

    def first_fromat(self) -> str:
        dflt = "%I:%M %p"
        i = self._cfg._get_nested(self.parent, "first_fromat", default=dflt)
        return i if isinstance(i, str) else dflt

    def second_format(self) -> str:
        dflt = "%A, %d %B %Y"
        i = self._cfg._get_nested(self.parent, "second-format", default=dflt)
        return i if isinstance(i, str) else dflt

    def anchor(self) -> str:
        dflt = "center left"
        i = self._cfg._get_nested(self.parent, "anchor", default=dflt)
        return i if isinstance(i, str) else dflt

    def layer(self) -> str:
        dflt = "bottom"
        i = self._cfg._get_nested(self.parent, "layer", default=dflt)
        return i if isinstance(i, str) else dflt
