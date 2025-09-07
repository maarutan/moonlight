from ...modules.clock import Clock
from .._config_handler import ConfigHandlerStatusBar


def clock_handler(cfg: ConfigHandlerStatusBar) -> Clock:
    return Clock(
        format=cfg.clock.get_clock(),
        is_horizontal=cfg.bar.is_horizontal(),
    )
