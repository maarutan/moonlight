from typing import TYPE_CHECKING
from utils.config_handler import ConfigHandler
from utils.constants import Const


if TYPE_CHECKING:
    from .menu import ScreenMenu


DEFAULT_SCREEN_MENU_CONFIG = lambda name: {
    name: {
        "enabled": True,
        "items": [
            {
                "icon": " 󰑓 ",
                "name": "Reload Moonlight",
                "cmd": f"bash -c 'kill -HUP $(cat {Const.APP_PID_FILE})'",
            }
        ],
    },
}


SCHEME_SCREEN_MENU_CONFIG = lambda name: {
    name: {
        "type:type": dict,
        "type:properties": {
            "enabled": {"type:type": bool},
            "items": {
                "type:type": list,
                "type:items": {
                    "type:type": dict,
                    "type:properties": {
                        "icon": {"type:type": str},
                        "name": {"type:type": str},
                        "cmd": {"type:type": str},
                    },
                    "type:required": ["icon", "name", "cmd"],
                },
            },
        },
        "type:required": ["enabled", "items"],
    }
}


class ScreenMenuConfig(ConfigHandler):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            config_path=Const.CONFIG_FILE,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / f"{name}.jsonc",
            default_config=DEFAULT_SCREEN_MENU_CONFIG(name),
            json_schema=SCHEME_SCREEN_MENU_CONFIG(name),
        )
