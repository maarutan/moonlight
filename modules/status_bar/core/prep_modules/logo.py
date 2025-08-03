from ...modules.logo import Logo
from .._config_handler import ConfigHandler


def logo_handler(cfg: ConfigHandler) -> Logo:
    return Logo(
        is_horizontal=cfg.bar.is_horizontal(),
        content=cfg.logo.content(),
        image_path=cfg.logo.image_path(),
        type=cfg.logo.type(),
        image_size=cfg.logo.image_size(),
    )
