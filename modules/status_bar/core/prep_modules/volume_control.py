from fabric.widgets.box import Box
from ...modules.volume_control import VolumeControl
from .._config_handler import ConfigHandler


def volume_control_handler(cfg: ConfigHandler) -> Box:
    return Box(children=VolumeControl())
