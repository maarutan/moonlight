from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandler


class StatusBarCfg:
    def __init__(self, cfg_handler: "ConfigHandler") -> None:
        self._cfg = cfg_handler

    def position(self) -> str:
        dflt = "left, top, right"
        position = self._cfg._get_options("position", "top")
        pos_map = {
            "top": "left, top, right",
            "bottom": "left, bottom, right",
            "left": "top, left, bottom",
            "right": "top, right, bottom",
        }
        return pos_map.get(position, dflt)  # type: ignore

    def margin(self) -> str:
        return str(self._cfg._get_options("margin", "0, 0, 0, 0"))

    def layer(self) -> str:
        return str(self._cfg._get_options("layer", "top"))

    def is_horizontal(self) -> bool:
        position = self.position()
        return position in ["left, top, right", "left, bottom, right"]
