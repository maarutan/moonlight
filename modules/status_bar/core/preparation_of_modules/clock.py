from ...modules.clock import Clock
from .._config_handler import ConfigHandler


def clock_handler(conf: ConfigHandler) -> Clock:
    return Clock(
        format=conf.get_clock(),
        orientation_pos=conf.is_horizontal(),
    )
