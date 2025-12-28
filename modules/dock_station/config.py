from utils.config_handler import ConfigHandler
from utils.constants import Const

DEFAULT_CONFIG = lambda name: {
    name: {
        "enabled": True,
        "layer": "top",
        "anchor": "bottom right",
        "margin": "0px 0px 0px 0px",
        "hover": {"thickness": 10, "max-width": 500},
        "icon-size": 32,
        "pinned": [],
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
            "hover": {
                "type:type": dict,
                "type:properties": {
                    "thickness": {"type:type": int},
                    "max-width": {"type:type": int},
                },
            },
            "icon-size": {"type:type": int},
            "pinned": {"type:type": list},
        },
    }
}


class DockStationConfig(ConfigHandler):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            config_path=Const.CONFIG_FILE,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / f"{name}.jsonc",
            default_config=DEFAULT_CONFIG(name),
            json_schema=SCHEME_CONFIG(name),
        )
