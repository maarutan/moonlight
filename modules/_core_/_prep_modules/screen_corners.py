from typing import TYPE_CHECKING
from modules import ScreenCorners

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def screen_corners_handler(cfg: "CoreConfigHandler") -> ScreenCorners:
    return ScreenCorners(
        enabled=cfg.screen_corners.enabled(),
    )
