from ...modules.cavalcade import SpectrumRender
from .._config_handler import ConfigHandlerStatusBar
from fabric.widgets.stack import Stack
from fabric.widgets.box import Box


def cavalcade_handler(cfg: ConfigHandlerStatusBar) -> Stack:
    cavalcade = SpectrumRender(is_horizontal=cfg.bar.is_horizontal())
    return Stack(children=[cavalcade.get_spectrum_box()])
