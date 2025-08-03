from ...modules.clock import Clock
from .._config_handler import ConfigHandler


def clock_handler(cfg: ConfigHandler) -> Clock:
    return Clock(
        format=cfg.clock.get_clock(),
        orientation_pos=cfg.bar.is_horizontal(),
    )
