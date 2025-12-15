from utils.config_handler import ConfigHandler
from utils.constants import Const

DEFAULT_CONFIG = lambda name: {
    name: {
        "enabled": True,
        "anchor": "top-right",
        "layer": "overlay",
        "margin": "8px 8px 8px 8px",
        "image-size": 64,
        "default-timeout": 5000,
        "max-width": 360,
        "urgency-size": 40,
        "max-chars-width": 30,
        "progress-bar-line-style": "round",
        "progress-bar-line-width": 20,
    }
}

SCHEME_CONFIG = lambda name: {
    name: {
        "type:type": dict,
        "type:properties": {
            "enabled": {"type:type": bool},
            "layer": {"type:type": str},
            "anchor": {"type:type": str},
            "margin": {"type:type": str},
            "image-size": {"type:type": int},
            "default-timeout": {"type:type": int},
            "max-width": {"type:type": int},
            "urgency-size": {"type:type": int},
            "max-chars-width": {"type:type": int},
            "progress-bar-line-style": {"type:enum": ["round", "square"]},
            "progress-bar-line-width": {"type:type": int},
        },
    }
}


class NotificationConfig(ConfigHandler):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            config_path=Const.CONFIG_FILE,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / f"{name}.jsonc",
            default_config=DEFAULT_CONFIG(name),
            json_schema=SCHEME_CONFIG(name),
        )
