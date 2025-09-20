from typing import TYPE_CHECKING
from modules.cava_desktop import CavaDesktop

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def cava_desktop_handler(cfg: "CoreConfigHandler") -> CavaDesktop:
    return CavaDesktop(
        enable=cfg.cava_desktop.enabled(),
    )
