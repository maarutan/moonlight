from utils.config_handler import ConfigHandler
from utils.constants import Const
from ..status_bar.bar import confh, widget_name

DEFAULT_MY_CORNER_CONFIG = lambda name: {
    name: {
        "enabled": True,
        "screen_corner": {
            "size": 40,
        },
        "my_corner": {
            "enabled": True,
            "size": 40,
        },
    }
}

MY_CORNER_SCHEMA = lambda name: {
    name: {
        "properties": {
            "enabled": {"type": bool},
            "screen_corner": {
                "type": dict,
                "properties": {
                    "size": {"type": int},
                },
            },
            "my_corner": {
                "type": dict,
                "properties": {
                    "enabled": {"type": bool},
                    "size": {"type": int},
                },
            },
        },
    },
}


class MyCornerConfig(ConfigHandler):
    def __init__(self, name: str) -> None:
        self.bar_wideget_name = widget_name
        self.confbar = confh
        super().__init__(
            name=name,
            config_path=Const.CONFIG_FILE,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / f"{name}.jsonc",
            default_config=DEFAULT_MY_CORNER_CONFIG(name),
            json_schema=MY_CORNER_SCHEMA(name),
        )
