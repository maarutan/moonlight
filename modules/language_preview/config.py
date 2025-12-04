from __future__ import annotations
from utils.config_handler import ConfigHandler
from utils.json_type_schema import anchor_type
from utils.constants import Const

DEFAULT_LANGUAGE_PREVIEW_CONFIG = lambda name: {
    name: {
        "enabled": True,
        "layer": "top",
        "margin": "40px 40px 40px 40px",
        "position": "center",
        "languages": {
            "us": "english",
            "ru": "russian",
            "pl": "polish",
            "kg": "kyrgyzstan",
            "kz": "kazakhstan",
            "uz": "uzbekistan",
        },
        "default_fullnames": {
            "us": "English",
        },
        "replacer": {"us": "en"},
    },
}

SCHEME_LANGUAGE_PREVIEW_CONFIG = lambda name: {
    name: {
        "type:type": dict,
        "type:properties": {
            "enabled": {"type:type": bool},
            "layer": {"type:enum": ["top", "bottom"]},
            "margin": {"type:type": str},
            "position": {"type:enum": anchor_type},
            "default_fullnames": {"type:type": dict},
            "replacer": {"type:type": dict},
        },
        "type:required": [
            "enabled",
            "layer",
            "margin",
            "position",
            "default_fullnames",
            "replacer",
        ],
    }
}


class LanguagePreviewConfig(ConfigHandler):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            config_path=Const.CONFIG_FILE,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / f"{name}.jsonc",
            default_config=DEFAULT_LANGUAGE_PREVIEW_CONFIG(name),
            json_schema=SCHEME_LANGUAGE_PREVIEW_CONFIG(name),
        )
