from ...modules.cava import SpectrumRender
from .._config_handler import ConfigHandler


def cava_handler(cfg: ConfigHandler) -> SpectrumRender:
    return SpectrumRender(cfg.bar.is_horizontal())
