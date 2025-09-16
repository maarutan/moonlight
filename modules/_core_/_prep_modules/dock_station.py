from typing import TYPE_CHECKING
from modules import Dock

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def dock_station_handler(cfg: "CoreConfigHandler") -> Dock:
    return Dock(enabled=cfg.dock_station.enabled())
