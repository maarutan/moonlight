from ...modules.language import Language
from .._config_handler import ConfigHandler


def language_handler(conf: ConfigHandler) -> Language:
    return Language(
        orientation_pos=conf.is_horizontal(),
        number_letters=conf.get_language_number_letters(),
        register=conf.get_language_register(),
    )
