import os
from pathlib import Path
from tempfile import gettempdir

CURRENT_DIR = Path(__file__).parent

"===== ~~ App ~~ ====="
APP_NAME = "moonlight"
APP_NAME_CAP = "MoonLight"

"===== ~~ Base Dir & Config ~~ ====="
HOME = Path.home()
DOT_CONFIG = HOME / ".config"
HYPR_CONFIG_DIR = DOT_CONFIG / "hypr"
APP_CONFIG_DIR = HYPR_CONFIG_DIR / APP_NAME
CONFIG_FILE = APP_CONFIG_DIR / "config.jsonc"
ASSETS = CURRENT_DIR.parent / "assets"


"===== ~~ Status Bar ~~ ====="
"status bar dir:"
STATUS_BAR_DIR = APP_CONFIG_DIR / "Status_Bar"
STATUS_BAR_CONFIG = STATUS_BAR_DIR / "config.jsonc"
STATUS_BAR_LOCK_MODULES = STATUS_BAR_DIR / ".modules-lock.json"

"===== ~~ Dock Station ~~ ====="
DOCK_STATION_DIR = APP_CONFIG_DIR / "Dock_Station"
DOCK_STATION_CONFIG = DOCK_STATION_DIR / "config.jsonc"

"===== ~~ cava config ~~ ====="
CAVA_CONFIG = CURRENT_DIR / "cavalcade" / "cava.ini"

"===== ~~ ASSETS ~~ ====="
PLACEHOLDER_IMAGE = ASSETS / "player" / "placeholder.png"
GHOST_IMAGE = ASSETS / "empty" / "ghost.png"
BACKBUTTON = ASSETS / "buttons" / "back.png"
URL_AVATAR = APP_CONFIG_DIR / "Assets" / "Profile" / "http(s)_avatar.png"
RESOLVED_ICONS = ASSETS / "resolved_icons.json"

"===== ~~ Templates ~~ ====="
TEMP_DIR = Path(gettempdir())
