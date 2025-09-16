from typing import TYPE_CHECKING
from modules import ActivateLinux

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def activate_linux_handler(cfg: "CoreConfigHandler") -> ActivateLinux:
    return ActivateLinux(
        enabled=cfg.activate_linux.enabled(),
    )
