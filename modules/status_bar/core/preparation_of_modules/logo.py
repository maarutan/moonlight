from ...modules.logo import Logo
from .._config_handler import ConfigHandler


def logo_handler(conf: ConfigHandler) -> Logo:
    return Logo(
        orientation_pos=conf.is_horizontal(),
        content=conf.get_logo(),
        image_path=conf.get_logo_path(),
        type_=conf.get_logo_type(),
        image_size=conf.get_logo_size(),
    )
