from typing import TYPE_CHECKING
from modules import DesktopClock

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def desktop_clock_handler(cfg: "CoreConfigHandler") -> DesktopClock:
    return DesktopClock(
        enabled=cfg.desktop_clock.enabled(),
        first_fromat=cfg.desktop_clock.first_fromat(),
        second_format=cfg.desktop_clock.second_format(),
        anchor=cfg.desktop_clock.anchor(),
        layer=cfg.desktop_clock.layer(),
    )
