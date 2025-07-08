from pathlib import Path

"===== ~~ App ~~ ====="
APP_NAME = "moonlight"
APP_NAME_CAP = "MoonLight"

"===== ~~ Base Dir & Config ~~ ====="
HOME = Path.home()
DOT_CONFIG = HOME / ".config"
HYPR_CONFIG_DIR = DOT_CONFIG / "hypr"
APP_CONFIG_DIR = HYPR_CONFIG_DIR / APP_NAME
CONFIG_FILE = APP_CONFIG_DIR / "config.jsonc"


"===== ~~ Status Bar ~~ ====="
"status bar dir:"
STATUS_BAR_DIR = APP_CONFIG_DIR / "Status_Bar"
STATUS_BAR_CONFIG = STATUS_BAR_DIR / "config.jsonc"
