from utils.configuration_handler import ConfigurationHandler


class ConfigHandlerStatusBar(ConfigurationHandler):
    def __init__(self):
        super().__init__()

        self.config = self.get_option("widgets.statusbar")
        self.config_modules = self.config["modules"]
        self.orientation = "v" if self.is_vertical() else "h"

    def is_vertical(self) -> bool:
        """Return True if bar is vertical (left or right anchor)."""
        return self.config["position"] in ("left", "right")

    def anchor(self) -> str:
        """Get anchor from config safely"""
        curr_pos = self.config.get("position", "top")
        anchor_map = {
            "top": "left top right",
            "bottom": "left bottom right",
            "left": "top left bottom",
            "right": "top right bottom",
        }
        return anchor_map.get(curr_pos, "left top right")
