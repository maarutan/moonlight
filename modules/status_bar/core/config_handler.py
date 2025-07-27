from pathlib import Path
from typing import Literal
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

    def get_corners(self) -> str:
        i = self._get_options("corners", 0)
        if isinstance(i, str):
            return str(i)
        return "0"

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

    def get_magic_icons(self) -> str:
        data = self._get_options("workspaces", {})
        if isinstance(data, dict):
            val = data.get("magic-icons")
            if isinstance(val, str):
                return val
        return "✨"

    def get_enable_buttons_factory(self) -> bool:
        data = self._get_options("workspaces", {})
        if isinstance(data, dict):
            val = data.get("enable-buttons_factory")
            if isinstance(val, bool):
                return val
        return True

    def get_enable_magic(self) -> bool:
        data = self._get_options("workspaces", {})
        if isinstance(data, dict):
            val = data.get("magic-view")
            if isinstance(val, bool):
                return val
        return True

    def get_layer(self) -> str:
        i = self._get_options("layer", "top")
        return str(i)

    def get_margin(self) -> str:
        i = self._get_options("margin", "0, 0, 0, 0")
        return str(i)

    def get_position_keyword(self) -> str:
        mapping = {
            "left, top, right": "top",
            "left, bottom, right": "bottom",
            "top, left, bottom": "left",
            "top, right, bottom": "right",
        }
        return mapping.get(self.get_position(), "top")

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
            i = i.get("image-path", "")
            return str(i)
        return ""

    def get_logo_size(self) -> int:
        i = self._get_options("logo", "")
        if isinstance(i, dict):
            i = i.get("image-size", 24)
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

    def get_tray_box(self) -> bool:
        i = self._get_options("tray", {})
        if isinstance(i, dict):
            i = i.get("tray-box", False)
            return bool(i)
        return False

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

        if isinstance(i, int):
            return i

        if isinstance(i, str) and i.isdigit():
            return int(i)

        return 12  # fallback

    "~~ language ~~"

    def get_language_number_letters(self) -> int:
        i = self._get_options("language", {})
        if isinstance(i, dict):
            i = i.get("number_letters", 2)
            return i
        return 2

    def get_language_register(self) -> Literal["upper", "u", "l", "lower"]:
        i = self._get_options("language", {})
        if isinstance(i, dict):
            i = i.get("register", "lower")
            return i
        return "lower"

    "~~ Tray Box ~~"

    def get_bar_position_for_tray_box(self) -> str:
        position = self._get_options("position", "top")
        if isinstance(position, str):
            return position
        return "top"

    def tray_box_position_handler(self) -> str:
        barpos = self.get_bar_position_for_tray_box()
        start = self.get_modules_start()
        center = self.get_modules_center()
        end = self.get_modules_end()

        if barpos == "top":
            if "tray" in start:
                return "top left"
            elif "tray" in center:
                return "top"
            elif "tray" in end:
                return "top right"

        elif barpos == "left":
            if "tray" in start:
                return "top left"
            elif "tray" in center:
                return "center left"
            elif "tray" in end:
                return "bottom left"

        elif barpos == "right":
            if "tray" in start:
                return "top right"
            elif "tray" in center:
                return "center right"
            elif "tray" in end:
                return "bottom right"

        if barpos == "bottom":
            if "tray" in start:
                return "bottom left"
            elif "tray" in center:
                return "bottom"
            elif "tray" in end:
                return "bottom right"
        return "top"

    "~~ title ~~"

    def get_truncation_title(self) -> bool:
        i = self._get_options("title", {})
        if isinstance(i, dict):
            i = i.get("truncate", False)
            return bool(i)
        return False

    def get_truncation_size_title(self) -> int:
        i = self._get_options("title", {})
        if isinstance(i, dict):
            i = i.get("truncate-size", 80)
            return int(i)
        return 80

    def get_title_map(self) -> list:
        i = self._get_options("title", {})
        if isinstance(i, dict):
            i = i.get("map", [])
            return i
        return []

    def get_enable_icon(self) -> bool:
        i = self._get_options("title", {})
        if isinstance(i, dict):
            i = i.get("icon_enable", False)
            return bool(i)
        return False

    def get_vertical_title_length(self) -> int:
        i = self._get_options("title", {})
        if isinstance(i, dict):
            i = i.get("vertical-length", 6)
            return int(i)
        return 6
