from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


class ActivateLinuxCfg:
    def __init__(self, cfg: "CoreConfigHandler"):
        self._cfg = cfg
        self.parent = "activate-linux"

    def enabled(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "enabled", default=dflt)
        return i if isinstance(i, bool) else dflt
