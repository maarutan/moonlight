from typing import Literal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class MetricsCfg:
    def __init__(self, _cfg: "ConfigHandlerStatusBar") -> None:
        self.parent = "metrics"
        self._cfg = _cfg

    def positions(self) -> list[str]:
        dflt = [
            "cpu",
            "ram",
            "disk",
        ]
        i = self._cfg._get_nested(self.parent, "positions", default=dflt)
        return i if isinstance(i, list) else dflt
