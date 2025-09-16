from typing import TYPE_CHECKING
from modules import StatusBar

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def status_bar_handler(cfg: "CoreConfigHandler") -> StatusBar:
    return StatusBar(
        enabled=cfg.status_bar.enabled(),
    )
