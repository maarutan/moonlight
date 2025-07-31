from ...modules.cava import SpectrumRender
from .._config_handler import ConfigHandler


def cava_handler(conf: ConfigHandler) -> SpectrumRender:
    return SpectrumRender(conf.is_horizontal())
