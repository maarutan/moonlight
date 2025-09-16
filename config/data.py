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
APP_CONFIG_FILE = APP_CONFIG_DIR / "config.jsonc"
CONFIG_FILE = APP_CONFIG_DIR / "config.jsonc"
ASSETS = CURRENT_DIR.parent / "assets"
DOCK_MENU_ICON = ASSETS / "Dock_Station" / "menu.png"
STYLES_DIR = CURRENT_DIR.parent / "styles"
MAIN_CSS_FILE = CURRENT_DIR.parent / "main.css"

"===== ~~ Status Bar ~~ ====="
"status bar dir:"
STATUS_BAR_DIR = APP_CONFIG_DIR / "Status_Bar"
STATUS_BAR_CONFIG = STATUS_BAR_DIR / "config.jsonc"
STATUS_BAR_LOCK_MODULES = STATUS_BAR_DIR / ".modules-lock.json"

"===== ~~ Dock Station ~~ ====="
DOCK_STATION_DIR = APP_CONFIG_DIR / "Dock_Station"
DOCK_STATION_CONFIG = DOCK_STATION_DIR / "config.jsonc"
DOCK_STATION_PINS = DOCK_STATION_DIR / "pinned.json"

"===== ~~ cava config ~~ ====="
CAVA_CONFIG = CURRENT_DIR / "cavalcade" / "cava.ini"

"===== ~~ ASSETS ~~ ====="

PLACEHOLDER_DIR = ASSETS / "placeholders"
PLACEHOLDER_IMAGE = PLACEHOLDER_DIR / "placeholder.png"
LOGOUT_SOUND_DIR = ASSETS / "logout_sound"
CHARGING_SOUND_DIR = ASSETS / "charging_sound"
DISCONNECT_CHARGING_SOUND = CHARGING_SOUND_DIR / "airpods_disconnected.mp3"
CHARGING_SOUND = CHARGING_SOUND_DIR / "ios_charging_sound.mp3"
LOGOUT_SOUND = LOGOUT_SOUND_DIR / "ios_lock_off_sound.mp3"

GHOST_IMAGE = ASSETS / "empty" / "ghost.png"
BACKBUTTON = ASSETS / "buttons" / "back.png"
APP_ASSETS = APP_CONFIG_DIR / "Assets"
BATTERY_ICONS = ASSETS / "battery"

"===== ~~ APP ASSETS ~~ ====="
URL_AVATAR = APP_ASSETS / "Profile" / "http(s)_avatar.png"
RESOLVED_ICONS = APP_ASSETS / "resolved_icons.json"
BASE_LOCK = APP_ASSETS / "base_lock.json"

"===== ~~ Templates ~~ ====="
TEMP_DIR = Path(gettempdir())
