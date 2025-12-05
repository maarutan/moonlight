from utils.config_handler import ConfigHandler
from utils.constants import Const


def DEFAULT_CONFIG(name: str) -> dict:
    return {
        "cavalade": {
            name: {
                "enabled": True,
                "general": {
                    "bars": 50,
                    "sensitivity": 100,
                    "framerate": 60,
                    "lower_cutoff_freq": 50,
                    "higher_cutoff_freq": 8000,
                    "autosens": 1,
                    "bar_width": 1,
                    "bar_spacing": 0,
                },
                "output": {
                    "method": "raw",
                    "raw_target": "/tmp/cava.fifo",
                    "bit_format": "16bit",
                    "channels": "stereo",
                },
                "smoothing": {
                    "gravity": 200,
                    "integral": 70,
                    "ignore": 0,
                    "monstercat": 1,
                },
                "eq": {
                    "1": 1.00,
                    "2": 1.00,
                    "3": 1.00,
                    "4": 1.00,
                    "5": 1.00,
                    "6": 1.00,
                    "7": 1.00,
                    "8": 1.00,
                    "9": 1.00,
                },
            }
        }
    }


def SCHEME_CONFIG(name: str) -> dict:
    return {
        "cavalade": {
            name: {
                "type:type": dict,
                "type:properties": {
                    "enabled": {"type:type": bool},
                },
            }
        }
    }


class CavaladeConfig(ConfigHandler):
    def __init__(self, widget_name: str):
        default = DEFAULT_CONFIG(widget_name)
        schema = SCHEME_CONFIG(widget_name)

        super().__init__(
            name="cavalade",
            config_path=Const.CONFIG_FILE,
            default_config_path=Const.DEFAULT_CONFIG_DIRECTORY / "cavalade.jsonc",
            default_config=default,
            json_schema=schema,
        )

        self.widget_name = widget_name

    def get_widget_config(self) -> dict:
        return self.config_data.get("cavalade", {}).get(self.widget_name, {})

    def get_option(self, keypath: str, default=None):
        if keypath.startswith("cavalade."):
            full = keypath
        else:
            full = f"cavalade.{self.widget_name}.{keypath}".rstrip(".")
        return super().get_option(full, default)
