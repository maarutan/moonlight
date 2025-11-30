import os
from pathlib import Path
from fabric import Application

from .language_preview.preview import LanguagePreview
from .settings.start_menu import StartMenu
from utils.constants import Const
from utils.decorators import singletonclass
from loguru import logger
from gi.repository import Gtk, Gdk  # pyright: ignore[reportMissingModuleSource]
from dartsass._main import _dart_sass_path, compile

from .status_bar.bar import StatusBar
from .screen_menu.menu import ScreenMenu
from .my_corner.corners import ScreenCorners


@singletonclass
class Handler:
    def __init__(self) -> None:
        modules = [
            ScreenMenu,
            ScreenCorners,
            StatusBar,
            LanguagePreview,
            # ----------- always last -----------
        ]

        Const.APP_PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

        self.windows = self._load_enabled_modules(modules)
        self.app = Application(Const.APPLICATION_NAME, *self.windows)

        self._scss_compile()

        self._apply_custom_stylesheet()
        self.app.set_stylesheet_from_file(Const.STYLESHEET_PATH.as_posix())

    def _load_enabled_modules(self, modules: list) -> list:
        """Load only enabled modules from provided list."""
        loaded = []
        for module in modules:
            if module is None:
                # Disabled modules (None)
                continue
            try:
                instance = module()
                loaded.append(instance)
            except Exception as e:
                logger.error(f"[{module.__name__}] Failed to initialize: {e}")
        return loaded

    def _apply_custom_stylesheet(self, widget: Gtk.Widget | None = None):
        """Apply custom stylesheet to windows except dialogs."""
        settings = Gtk.Settings.get_default()
        if settings:
            settings.set_property("gtk-theme-name", "Default")
            settings.set_property("gtk-application-prefer-dark-theme", False)

        if widget and isinstance(widget, Gtk.Dialog):
            return

        provider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()  # type: ignore

        Gtk.StyleContext.add_provider_for_screen(  # type: ignore
            screen,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 100,
        )

    def _scss_compile(self):
        sass_bin = Path(_dart_sass_path)
        if not os.access(sass_bin, os.X_OK):
            os.chmod(sass_bin, 0o755)
            logger.info(
                f"Updated sass executable permissions to {os.stat(sass_bin).st_mode}"
            )
        compile(
            filenames=(
                Const.CURRENT_STYLE_MAIN.as_posix(),
                Const.STYLESHEET_PATH.as_posix(),
            )
        )
