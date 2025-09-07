from ...modules.language import Language
from .._config_handler import ConfigHandlerStatusBar


def language_handler(cfg: ConfigHandlerStatusBar) -> Language:
    return Language(
        is_horizontal=cfg.bar.is_horizontal(),
        number_letters=cfg.language.number_letters(),
        register=cfg.language.register(),
    )
