from utils.config_handler import ConfigHandler
from utils.constants import Const

DEFAULT_ACTIVATE_LINUX_CONFIG = lambda name: {
    name: {
        "enabled": True,
        "layer": "bottom",
        "anchor": "bottom right",
        "margin": "0px 70px 70px 0px",
    }
}

SCHEME_ACTIVATE_LINUX_CONFIG = lambda name: {
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


class ActivateLinuxConfig(ConfigHandler):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            config_path=Const.CONFIG_FILE,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / f"{name}.jsonc",
            default_config=DEFAULT_ACTIVATE_LINUX_CONFIG(name),
            json_schema=SCHEME_ACTIVATE_LINUX_CONFIG(name),
        )
