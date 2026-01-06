from typing import Any, Dict
from utils.configuration_handler import ConfigurationHandler
from .modules.anchors import ANCH_DICT


class ConfigHandlerDockStation(ConfigurationHandler):
    def __init__(self):
        super().__init__()
        cfg = self.get_option("widgets.dockstation") or {}
        self.config: Dict[str, Any] = cfg if isinstance(cfg, dict) else {}
        self.orientation = "v" if self.is_vertical() else "h"

    def is_vertical(self) -> bool:
        return self.config["anchor"].endswith("left") or self.config["anchor"].endswith(
            "right"
        )

    def _anchor_handler(self) -> str:
        anchor_side = "bottom"
        anchor = self.config["anchor"]
        for key, value in ANCH_DICT.items():
            if anchor in value:
                anchor_side = key
                break
        return anchor_side
