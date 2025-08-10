from ...modules.cava import SpectrumRender
from .._config_handler import ConfigHandler
from fabric.widgets.stack import Stack
from fabric.widgets.box import Box


def cava_handler(cfg: ConfigHandler) -> Stack:
    cava = SpectrumRender(is_horizontal=cfg.bar.is_horizontal())
    return Stack(children=[cava.get_spectrum_box()])
