from typing import TYPE_CHECKING
from modules import LanguagePreview

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def language_preview_handler(cfg: "CoreConfigHandler") -> LanguagePreview:
    return LanguagePreview(
        enabled=cfg.language_preview.enabled(),
        default_fullnames=cfg.language_preview.default_fullnames(),
        margin=cfg.language_preview.margin(),
        layer=cfg.language_preview.layer(),
        position=cfg.language_preview.position(),
        replacer=cfg.language_preview.replacer(),
    )
