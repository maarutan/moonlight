from pathlib import Path
from utils import JsonManager as jsonc
from utils import FileManager
from .default_config import configuration
from config import (
    STATUS_BAR_DIR,
    STATUS_BAR_CONFIG,
)


class ConfigHandler:
    def __init__(self) -> None:
        self.jsonc = jsonc()
        self.fm = FileManager()
        self.path = Path(STATUS_BAR_CONFIG)
        self.fm.if_not_exists_create(STATUS_BAR_DIR)

    "~~ Config ~~"

    def generate_default_config(self) -> None:
        if self.fm.read(self.path) in [None, ""]:
            self.fm.write(self.path, configuration)

    "~~ Options ~~"

    def _get_options(
        self,
        key: str,
        default: str | int | bool | dict | list | None = None,
    ) -> str | int | bool | dict | list | None:
        data = self.jsonc.read(self.path)
        return data.get(key, default)

    "~~ Bar ~~"

    def get_position(self) -> str:
        position = self._get_options("position", "top")

        if position == "top":
            return "left, top, right"

        elif position == "bottom":
            return "left, bottom, right"

        elif position == "left":
            return "top, left, bottom"

        elif position == "right":
            return "top, right, bottom"
        else:
            return "left, top, right"

    def is_horizontal(self) -> bool:
        position = self.get_position()
        horizontal_positions = ["left, top, right", "left, bottom, right"]
        vertical_positions = ["top, left, bottom", "top, right, bottom"]

        if position in horizontal_positions:
            return True
        elif position in vertical_positions:
            return False
        else:
            raise ValueError(f"Unknown position: {position}")

    def get_maximum_value(self) -> int:
        data = self._get_options("workspaces", {})
        if isinstance(data, dict):
            val = data.get("maximum-values")
            if isinstance(val, int):
                return val
        return 10

    def get_workspaces_numbering(self) -> list[str]:
        data = self._get_options("workspaces", {})
        if isinstance(data, dict):
            val = data.get("numbering-workpieces")
            if isinstance(val, list) and all(isinstance(x, str) for x in val):
                return val
        default_values = self.get_maximum_value()
        return [str(i) for i in range(1, default_values + 1)]

    def get_layer(self) -> str:
        i = self._get_options("layer", "top")
        return str(i)

    def get_margin(self) -> str:
        i = self._get_options("margin", "0, 0, 0, 0")
        return str(i)

    "~~ Logo ~~"

    def get_logo(self) -> str:
        i = self._get_options("logo", "")
        if isinstance(i, dict):
            i = i.get("content", "")
            return str(i)
        return "logo"

    def get_logo_path(self) -> str:
        i = self._get_options("logo", "")
        if isinstance(i, dict):
            i = i.get("image_path", "")
            return str(i)
        return ""

    def get_logo_size(self) -> int:
        i = self._get_options("logo", "")
        if isinstance(i, dict):
            i = i.get("image_size", 24)
            return int(i)
        return 24

    def get_logo_type(self) -> str:
        i = self._get_options("logo", "")
        if isinstance(i, dict):
            i = i.get("type", "")
            return str(i)
        return ""

    "~~ Modules ~~"

    def get_modules_center(self) -> list[str]:
        i = self._get_options("modules-center", [])
        return i if isinstance(i, list) else []

    def get_modules_end(self) -> list[str]:
        i = self._get_options("modules-end", [])
        return i if isinstance(i, list) else []

    def get_modules_start(self) -> list[str]:
        i = self._get_options("modules-start", [])
        return i if isinstance(i, list) else []

    "~~ Tray ~~"

    def get_tray_icon_size(self) -> int:
        i = self._get_options("tray", {})
        if isinstance(i, dict):
            i = i.get("icon-size", 24)
            return int(i)
        return 24

    def get_tray_refresh_interval(self) -> int:
        i = self._get_options("tray", {})
        if isinstance(i, dict):
            i = i.get("refresh-interval", 1)
            return int(i)
        return 1

    def get_tray_spacing(self) -> int:
        i = self._get_options("tray", {})
        if isinstance(i, dict):
            i = i.get("spacing", 8)
            return int(i)
        return 8

    "~~ Memory ~~"

    def get_memory_format(self) -> str:
        i = self._get_options("memory", {})
        dflt = "{used:0.1f}G/{total:0.1f}G"
        if isinstance(i, dict):
            i = i.get("format")
            return str(i)
        return dflt

    def get_memory_interval(self) -> int:
        i = self._get_options("memory", {})
        if isinstance(i, dict):
            i = i.get("interval", 2)
            return int(i)
        return 2

    def get_memory_icon(self) -> str:
        i = self._get_options("memory", {})
        if isinstance(i, dict):
            i = i.get("icon", "")
            return i
        return ""

    "~~ clock ~~"

    def get_clock(self) -> int:
        i = self._get_options("clock", 12)
        return int(i)


# ch = ConfigHandler()
#
# ch.generate_default_config()
