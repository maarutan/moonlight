from fabric.utils.helpers import GLib
from pathlib import Path
from tempfile import gettempdir


class Const:
    # ---------------------------------------------------------------------
    # ---
    # --
    # -

    APPLICATION_NAME = "moonlight"

    SYSTEM_CACHE_DIRECTORY = Path(GLib.get_user_cache_dir())
    APP_CACHE_DIRECTORY = SYSTEM_CACHE_DIRECTORY / APPLICATION_NAME

    HOME_DIRECTORY = Path(GLib.get_home_dir())
    CONFIG_DIRECTORY = Path(GLib.get_user_config_dir())
    HYPRLAND_CONFIG_DIRECTORY = CONFIG_DIRECTORY / "hypr"
    HYPRLAND_APP_CONFIG_DIRECTORY = HYPRLAND_CONFIG_DIRECTORY / APPLICATION_NAME
    PROJECT_DIRECTORY = Path(__file__).parent.parent
    ASSETS_DIRECTORY = PROJECT_DIRECTORY / "assets"
    STYLESHEET_PATH = ASSETS_DIRECTORY / "styles" / "main.css"
    APP_ASSETS_DIRECTORY = HYPRLAND_APP_CONFIG_DIRECTORY / "Assets"
    APP_ASSETS_PROFILE_DIR = APP_ASSETS_DIRECTORY / "Profile"
    PROFILE_LOGO = APP_ASSETS_PROFILE_DIR / "http(s)_avatar.png"
    APP_ICONS_DIRECTORY = ASSETS_DIRECTORY / "app_icons"

    DEFAULT_CONFIG_DIRECTORY = PROJECT_DIRECTORY / "configs"
    LANGUAGE_PREVIEW_CONFIG = (
        HYPRLAND_APP_CONFIG_DIRECTORY / "Language_Preview" / "config.jsonc"
    )
    DEFAULT_APP_CONFIG = DEFAULT_CONFIG_DIRECTORY / "config.jsonc"
    JSON_SCHEMA_DIR = DEFAULT_CONFIG_DIRECTORY / "schemas"

    STATUS_BAR_DIR = (
        HYPRLAND_APP_CONFIG_DIRECTORY / HYPRLAND_APP_CONFIG_DIRECTORY / "Status_Bar"
    )
    STATUS_BAR_CONFIG = STATUS_BAR_DIR / "config.jsonc"

    PLACEHOLDERS_DIRECTORY = ASSETS_DIRECTORY / "placeholders"
    PLACEHOLDER_IMAGE_GHOST = PLACEHOLDERS_DIRECTORY / "ghost.png"
    TEMP_DIRECTORY = Path(gettempdir())

    CURRENT_STYLE_DIRECTORY = STYLESHEET_PATH.parent / "scss"
    CURRENT_STYLE_MAIN = CURRENT_STYLE_DIRECTORY / "import.scss"
    CURRENT_STYLE_STATUS_BAR = CURRENT_STYLE_DIRECTORY / "status_bar"
    CURRENT_STYLE_STATUS_BAR_WORKSPACE = CURRENT_STYLE_STATUS_BAR / "_workspaces.scss"

    CONFIG_STYLES_STATUSBAR_WORKSPACE = (
        DEFAULT_CONFIG_DIRECTORY / "styles" / "status_bar"
    )

    APP_PID_FILE = TEMP_DIRECTORY / APPLICATION_NAME / "moonlight.pid"
    APP_IS_RUNNING = APP_PID_FILE.parent / "is_running.txt"
    SCREEN_MENU_CONFIG = (
        HYPRLAND_APP_CONFIG_DIRECTORY / "Screen_Menu" / "screen_menu.jsonc"
    )

    MY_CORNER_CONFIG = HYPRLAND_APP_CONFIG_DIRECTORY / "My_Corner" / "corners.jsonc"
    THEME_SCSS = CURRENT_STYLE_DIRECTORY / "_theme.scss"
    BATTERY_ICONS_DIR = ASSETS_DIRECTORY / "battery"
    BATTERY_ICON_SVG = BATTERY_ICONS_DIR / "battery.svg"
    BATTERY_CHARGING_SOUND = BATTERY_ICONS_DIR / "charging.mp3"
    BATTERY_DISCHARGING_SOUND = BATTERY_ICONS_DIR / "discharging.mp3"

    CONFIG_FILE = HYPRLAND_APP_CONFIG_DIRECTORY / "config.jsonc"

    LOCAL_DIR = HOME_DIRECTORY / ".local" / "share" / APPLICATION_NAME
    CAVA_LOCAL_DIR = LOCAL_DIR / "cavalade"
    CAVA_DEFAULT_CONFIG = DEFAULT_CONFIG_DIRECTORY / "cavalade" / "cava.ini"
    APP_LAUNCHER_PID = TEMP_DIRECTORY / APPLICATION_NAME / "app_launcher.pid"
    FONT_DIR_ASSETS = ASSETS_DIRECTORY / "fonts"

    # -
    # --
    # ---
    # ---------------------------------------------------------------------

    @classmethod
    def init(cls):
        _auto_create_paths(cls)

    @classmethod
    def add_const(cls, name: str, path: Path):
        if hasattr(cls, name):
            raise ValueError(f"Const '{name}' already exists!")

        if not isinstance(path, Path):
            raise TypeError("path must be a pathlib.Path instance")

        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)

        setattr(cls, name, path)

        return path


def _auto_create_paths(cls: type):
    for _, value in cls.__dict__.items():
        if isinstance(value, Path):
            if value.suffix:
                value.parent.mkdir(parents=True, exist_ok=True)
                value.touch(exist_ok=True)
            else:
                value.mkdir(parents=True, exist_ok=True)


_auto_create_paths(Const)
