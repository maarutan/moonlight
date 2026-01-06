import os
from fabric.utils import GLib
from tempfile import gettempdir
from pathlib import Path


class Const:
    # ---------------------------------------------------------------------

    APP_NAME = "moonlight"

    PROJECT_ROOT = Path(__file__).parent.parent
    HOME = Path.home()

    # Basic XDG Variables
    XDG_CONFIG_HOME = Path(os.getenv("XDG_CONFIG_HOME", GLib.get_user_config_dir()))
    XDG_CACHE_HOME = Path(os.getenv("XDG_CACHE_HOME", GLib.get_user_cache_dir()))
    XDG_DATA_HOME = Path(os.getenv("XDG_DATA_HOME", GLib.get_user_data_dir()))

    # Basic App Directory
    APP_CONFIG_DIR = XDG_CONFIG_HOME / APP_NAME
    APP_CONFIG_FILE = (
        APP_CONFIG_DIR / "config.jsonc"
    )  # INFO: utils.configuration_handler
    APP_CACHE_DIR = XDG_CACHE_HOME / APP_NAME
    APP_DATA_DIR = XDG_DATA_HOME / APP_NAME

    DEFULT_CONFIG_DIR = PROJECT_ROOT / "config"
    DEFAULT_CONFIG_FILE = (
        DEFULT_CONFIG_DIR / "config.jsonc"
    )  # INFO: utils.configuration_handler
    DEFAULT_CONFIG_FILE_SCHEMA = DEFULT_CONFIG_DIR / "config_schema.json"

    TEMP_DIR = Path(gettempdir()) / APP_NAME
    APP_PID_FILE = TEMP_DIR / "app.pid"

    # Assets
    ASSETS_DIR = PROJECT_ROOT / "assets"
    # ICONS_DIR = ASSETS_DIR / "icons"

    # Placeholder
    PLACEHOLDER_DIR = ASSETS_DIR / "placeholder"
    PLACEHOLDER_IMAGE_GHOST = PLACEHOLDER_DIR / "ghost.png"

    # Styles
    STYLESHEET_DIR = ASSETS_DIR / "styles"
    STYLESHEET_MAIN = STYLESHEET_DIR / "main.css"
    STYLESHEET_SCSS_DIR = STYLESHEET_DIR / "scss"
    STYLESHEET_SCSS = STYLESHEET_SCSS_DIR / "import.scss"

    # Gtk default theme
    STYLESHEET_DEFAULT_GTK = STYLESHEET_DIR / "gtk" / "default.css"

    @classmethod
    def init(cls):
        _auto_create_paths(cls)


def _auto_create_paths(cls: type):
    for _, value in cls.__dict__.items():
        if isinstance(value, Path):
            if value.suffix:
                value.parent.mkdir(parents=True, exist_ok=True)
                value.touch(exist_ok=True)
            else:
                value.mkdir(parents=True, exist_ok=True)


_auto_create_paths(Const)
