from utils.config_handler import ConfigHandler
from utils.constants import Const
from utils.json_type_schema import block_position


DEFAULT_STATUSBAR_CONFIG = lambda name: {
    name: {
        "enabled": True,
        "position": "top",
        "layer": "top",
        "margin": "0px 0px 0px 0px",
        "transparent": False,
        "if-vertical": {},
        "widgets": {
            "layout": {
                "start": ["workspaces"],
                "center": ["datetime"],
                "end": [],
            },
            "workspaces": {
                "style": {
                    "theme": "gnome",
                    "custom-style-path": "",
                },
                "max-visible-workspaces": 5,
                "enable-buttons-factory": True,
                "numbering-enabled": False,
                "numbering": [
                    "一",
                    "二",
                    "三",
                    "四",
                    "五",
                    "六",
                    "七",
                    "八",
                    "九",
                    "〇",
                ],
                "workspace-preview": {
                    "enabled": True,
                    "size": 400,
                    "event": "hover",
                    "event_click": "right",
                    "missing-behavior": "hide",
                },
                "magic-workspace": {"enabled": True, "icon": "✨"},
                "if-vertical": {},
            },
            "battery": {
                "procentage": {
                    "enabled": True,
                    "position": "left",
                    "event": "hover",
                },
                "if-vertical": {},
            },
            "network-speed": {
                "status": {
                    "download": {"show": "true", "icon": "󰇚"},
                    "upload": {"show": "false", "icon": "󰕒"},
                },
                "if-vertical": {},
            },
            "clock": {
                "format": "%I:%M %p",
                "if-vertical": {
                    "format": "%I\n%M\n%p",
                },
            },
            "system-tray": {
                "collapse": {
                    "enabled": False,
                    "columns": 4,
                    "button-size": 24,
                },
                "icon-size": 32,
                "if-vertical": {},
            },
            "language": {
                "number-letters": 2,
                "register": "lower",
                "if-vertical": {},
            },
            "window-title": {
                "type": "class",
                "vertical-length": 3,
                "title-length": 20,
                "unknown-title": "(づ｡◕‿‿◕｡)づ",
                "icon": {
                    "enabled": True,
                    "size": 32,
                    "position": "left",
                },
                "if-vertical": {},
            },
            "custom": {},
        },
    }
}

workspace_orientation_schema = {
    "type:type": dict,
    "type:properties": {
        "style": {
            "type:type": dict,
            "type:properties": {
                "theme": {"type:type": str},
                "custom-style-path": {"type:type": str},
            },
        },
        "max-visible-workspaces": {"type:type": int},
        "enable-buttons-factory": {"type:type": bool},
        "numbering-enabled": {"type:type": bool},
        "numbering": {"type:type": list, "type:items": {"type:type": str}},
        "magic-workspace": {
            "type:type": dict,
            "type:properties": {
                "enabled": {"type:type": bool},
                "icon": {"type:type": str},
            },
        },
        "workspace-preview": {
            "type:type": dict,
            "type:properties": {
                "enabled": {"type:type": bool},
                "size": {"type:type": int},
                "event": {"type:enum": ["hover", "click"]},
                "event_click": {"type:enum": ["left", "middle", "right"]},
                "missing-behavior": {"type:enum": ["show", "hide"]},
            },
        },
    },
}

SCHEME_STATUS_BAR_CONFIG = lambda name: {
    name: {
        "type:type": dict,
        "type:properties": {
            "enabled": {"type:type": bool},
            "position": {"type:enum": block_position},
            "layer": {"type:enum": ["top", "bottom"]},
            "margin": {"type:type": str},
            "transparent": {"type:type": bool},
            "if-vertical": {
                "type:type": dict,
                "type:properties": {
                    "layer": {"type:enum": ["top", "bottom"]},
                    "margin": {"type:type": str},
                    "transparent": {"type:type": bool},
                },
            },
            "widgets": {
                "type:type": dict,
                "type:properties": {
                    "layout": {
                        "type:type": dict,
                        "type:properties": {
                            "start": {
                                "type:type": list,
                                "type:items": {"type:type": str},
                            },
                            "center": {
                                "type:type": list,
                                "type:items": {"type:type": str},
                            },
                            "end": {
                                "type:type": list,
                                "type:items": {"type:type": str},
                            },
                        },
                    },
                    "workspaces": {
                        "type:type": dict,
                        "type:properties": {
                            **workspace_orientation_schema["type:properties"],
                            "if-vertical": {
                                "type:type": dict,
                                "type:properties": {
                                    **workspace_orientation_schema["type:properties"],
                                },
                            },
                        },
                    },
                    "battery": {
                        "type:type": dict,
                        "type:properties": {
                            "procentage": {
                                "type:type": dict,
                                "type:properties": {
                                    "enabled": {"type:type": bool},
                                    "position": {"type:enum": ["left", "right"]},
                                    "event": {"type:enum": ["hover", "show"]},
                                },
                            },
                            "if-vertical": {
                                "type:type": dict,
                                "type:properties": {
                                    "enabled": {"type:type": bool},
                                    "position": {"type:enum": ["left", "right"]},
                                    "event": {"type:enum": ["hover", "show"]},
                                },
                            },
                        },
                        "type:required": ["procentage"],
                    },
                    "network-speed": {
                        "type:type": dict,
                        "type:properties": {
                            "status": {
                                "type:type": dict,
                                "type:properties": {
                                    "download": {
                                        "type:type": dict,
                                        "type:properties": {
                                            "show": {"type:type": bool},
                                            "icon": {"type:type": str},
                                        },
                                    },
                                    "upload": {
                                        "type:type": dict,
                                        "type:properties": {
                                            "show": {"type:type": bool},
                                            "icon": {"type:type": str},
                                        },
                                    },
                                },
                            },
                            "if-vertical": {
                                "type:type": dict,
                                "type:properties": {},
                            },
                        },
                    },
                    "clock": {
                        "type:type": dict,
                        "type:properties": {
                            "format": {"type:type": str},
                            "if-vertical": {
                                "type:type": dict,
                                "type:properties": {},
                            },
                        },
                    },
                    "system-tray": {
                        "type:type": dict,
                        "type:properties": {
                            "collapse": {
                                "type:type": dict,
                                "type:properties": {
                                    "enabled": {"type:type": bool},
                                    "columns": {"type:type": int},
                                    "button-size": {"type:type": int},
                                },
                            },
                            "icon-size": {"type:type": int},
                            "if-vertical": {
                                "type:type": dict,
                                "type:properties": {
                                    "collapse": {
                                        "type:type": dict,
                                        "type:properties": {
                                            "enabled": {"type:type": bool},
                                            "columns": {"type:type": int},
                                            "button-size": {"type:type": int},
                                        },
                                    },
                                    "icon-size": {"type:type": int},
                                },
                            },
                        },
                        "type:required": ["collapse", "icon-size"],
                    },
                    "language": {
                        "type:type": dict,
                        "type:properties": {
                            "number-letters": {"type:type": int},
                            "register": {"type:enum": ["lower", "upper"]},
                            "if-vertical": {
                                "type:type": dict,
                                "type:properties": {
                                    "number-letters": {"type:type": int},
                                    "register": {"type:enum": ["lower", "upper"]},
                                },
                            },
                        },
                        "type:required": ["number-letters", "register"],
                    },
                    "window-title": {
                        "type:type": dict,
                        "type:properties": {
                            "type": {"type:enum": ["class", "title"]},
                            "vertical-length": {"type:type": int},
                            "title-length": {"type:type": int},
                            "unknown-title": {"type:type": str},
                            "icon": {
                                "type:type": dict,
                                "type:properties": {
                                    "enabled": {"type:type": bool},
                                    "size": {"type:type": int},
                                    "position": {"type:enum": ["left", "right"]},
                                },
                            },
                            "if-vertical": {
                                "type:type": dict,
                                "type:properties": {
                                    "type": {"type:enum": ["class", "title"]},
                                    "vertical-length": {"type:type": int},
                                    "title-length": {"type:type": int},
                                    "unknown-title": {"type:type": str},
                                    "icon": {
                                        "type:type": dict,
                                        "type:properties": {
                                            "enabled": {"type:type": bool},
                                            "size": {"type:type": int},
                                            "position": {
                                                "type:enum": ["left", "right"]
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "type:required": [
                            "type",
                            "vertical-length",
                            "title-length",
                            "icon",
                        ],
                    },
                    "custom": {"type:type": dict},
                },
            },
        },
        "type:required": ["enabled", "position", "widgets"],
    }
}


class StatusBarConfig(ConfigHandler):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            config_path=Const.STATUS_BAR_CONFIG,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / f"{name}.jsonc",
            default_config=DEFAULT_STATUSBAR_CONFIG(name),
            json_schema=SCHEME_STATUS_BAR_CONFIG(name),
        )
        self.debug = True
