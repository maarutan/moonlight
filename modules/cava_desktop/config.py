from utils.config_handler import ConfigHandler
from utils.constants import Const

DEFAULT_CONFIG = lambda name: {
    name: {
        "enabled": True,
        "layer": "bottom",
        "anchor": "top-left",
        "margin": "0px 40px 40px 50px",
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
        },
    }
}


class CavaDesktopConfig(ConfigHandler):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            config_path=Const.CONFIG_FILE,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / f"{name}.jsonc",
            default_config=DEFAULT_CONFIG(name),
            json_schema=SCHEME_CONFIG(name),
        )
