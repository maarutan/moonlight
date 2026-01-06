from pathlib import Path
from typing import TYPE_CHECKING
import tempfile
import os
from dartsass._main import _dart_sass_path, compile
from utils.constants import Const
from loguru import logger
from fabric.utils import idle_add, Gtk, Gdk

if TYPE_CHECKING:
    from .widgets_handler import WidgetsHandler


class Stylesheet:
    """
    Compile SCSS -> CSS, append user overrides (if provided), and apply final CSS to GTK via CssProvider.
    If the config's stylesheet_file is empty ("" or None) we IGNORE user overrides.
    """

    def __init__(self, widget_handler: "WidgetsHandler") -> None:
        self.widget_handler = widget_handler
        self.confh = widget_handler.confh

        # Clear theme flags early (optional)
        self._clear_gtk_theme()
        # self.load_default_css()

        # Set font and colorscheme
        self.set_fonts()
        self.set_colorscheme()

        # Compile SCSS -> produce Const.STYLESHEET_MAIN (expected)
        try:
            self._scss_compile()
        except Exception as e:
            logger.error(f"SCSS compilation failed: {e}")

        # Build combined css (main + user if present) and apply to GTK on the main loop

        try:
            combined_path = self._build_combined_css()
            # schedule apply on the GTK main loop (idle)
            self._apply_provider_from_file(combined_path)
        except Exception as e:
            logger.exception(f"Failed to build/apply combined stylesheet: {e}")

    # ----------------------------
    # SCSS compile
    # ----------------------------
    def _scss_compile(self) -> None:
        """Compile SCSS to CSS using Dart Sass (dartsass.compile wrapper)."""
        sass_bin = Path(_dart_sass_path)
        if not os.access(sass_bin, os.X_OK):
            try:
                os.chmod(sass_bin, 0o755)
                logger.info("Updated sass executable permissions.")
            except Exception as e:
                logger.warning(f"Failed to chmod sass binary: {e}")

        try:
            compile(
                filenames=(
                    Const.STYLESHEET_SCSS.as_posix(),
                    Const.STYLESHEET_MAIN.as_posix(),
                )
            )
            logger.info("SCSS compiled successfully.")
        except Exception as e:
            logger.error(f"SCSS compilation error: {e}")
            raise

    # ----------------------------
    # Build combined CSS
    # ----------------------------
    def _build_combined_css(self) -> Path:
        """
        Read compiled main CSS and user overrides (if configured and valid),
        produce a combined temporary CSS file. Returns path to that temp file.
        """

        # --- determine user override path (if any) ---
        conf = getattr(self.confh, "config", None)
        raw_user = None
        if isinstance(conf, dict):
            raw_user = conf.get("stylesheet-file", None)

        # If user didn't provide a path or provided empty string -> ignore overrides
        if not raw_user or (isinstance(raw_user, str) and raw_user.strip() == ""):
            user_path = None
            logger.debug(
                "No user stylesheet configured (empty or missing) -> skipping user overrides."
            )
        else:
            user_path = Path(raw_user).expanduser()

        user_css = ""
        # If user_path present, validate and ensure file exists (or create template)
        if user_path:
            if user_path.exists() and user_path.is_dir():
                logger.warning(f"User stylesheet is a directory, ignoring: {user_path}")
                user_path = None
            else:
                # ensure parent dir exists
                user_path.parent.mkdir(parents=True, exist_ok=True)
                if not user_path.exists():
                    # create template file
                    template = (
                        "/* User overrides for yourbar\n"
                        "   Add CSS rules here to override defaults.\n"
                        "   Example:\n"
                        "   .statusbar { background: #ff0000; }\n"
                        "*/\n\n"
                    )
                    try:
                        user_path.write_text(template, encoding="utf-8")
                        logger.info(f"Created user stylesheet template: {user_path}")
                    except Exception as e:
                        logger.warning(
                            f"Unable to create user stylesheet template {user_path}: {e}"
                        )
                        user_path = None

            # read user css if file present and readable
            if user_path and user_path.exists() and user_path.is_file():
                try:
                    user_css = user_path.read_text(encoding="utf-8")
                except Exception as e:
                    logger.warning(f"Failed reading user stylesheet {user_path}: {e}")
                    user_css = ""

        # Read compiled main CSS (produced by SCSS compile)
        main_css_path = Path(Const.STYLESHEET_MAIN)
        if not main_css_path.exists():
            logger.warning(f"Compiled main stylesheet not found: {main_css_path}")
            main_css = ""
        else:
            try:
                main_css = main_css_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed reading main stylesheet {main_css_path}: {e}")
                main_css = ""

        # Combine: main first; append user overrides only if user_css not empty
        if user_css and user_css.strip():
            combined = f"{main_css}\n\n/* ---- User overrides: {user_path} ---- */\n{user_css}\n"
        else:
            combined = main_css

        # Write combined to an atomic temp file and return its Path
        tmp_fd, tmp_path = tempfile.mkstemp(prefix="yourbar_combined_", suffix=".css")
        os.close(tmp_fd)
        tmp_path = Path(tmp_path)
        try:
            tmp_path.write_text(combined, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to write combined CSS to {tmp_path}: {e}")
            raise

        return tmp_path

    def set_fonts(self):
        font = self.confh.config["font"]
        font_size = self.confh.config["font-size"]

        style = f"""
        * {{
          font-family: {font};
          font-size: {font_size}px;
        }}
        """

        Path(Const.STYLESHEET_SCSS_DIR / "_font.scss").write_text(style)

    def set_colorscheme(self):
        colorscheme = Path(self.confh.config["theme"])
        theme = Const.STYLESHEET_SCSS_DIR / "themes" / f"{colorscheme}.scss"
        Path(Const.STYLESHEET_SCSS_DIR / "_theme.scss").write_text(theme.read_text())

    # ----------------------------
    # Apply CSS to GTK
    # ----------------------------
    def _apply_provider_from_file(self, css_path: Path) -> None:
        """
        Load CSS from a file into a CssProvider and add it to the screen.
        This function is intended to be called on the GTK main loop (via idle_add).
        """
        try:
            css_bytes = css_path.read_bytes()
        except Exception as e:
            logger.error(f"Failed to read combined CSS {css_path}: {e}")
            return

        provider = Gtk.CssProvider()
        try:
            provider.load_from_data(css_bytes)  # type: ignore
        except Exception as e:
            logger.error(f"CssProvider failed to load data: {e}")
            return

        screen = Gdk.Screen.get_default()  # type: ignore
        if screen is None:
            logger.warning("No Gdk.Screen available; cannot apply stylesheet.")
            return

        Gtk.StyleContext.add_provider_for_screen(  # type: ignore
            screen,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 100,
        )
        logger.info("Applied combined stylesheet to screen.")

    # ----------------------------
    # Optional helpers
    # ----------------------------
    def _clear_gtk_theme(self, widget: Gtk.Widget | None = None) -> None:
        """
        Prefer application stylesheet and enable dark theme by default.
        """
        settings = Gtk.Settings.get_default()
        if settings:
            try:
                settings.set_property("gtk-theme-name", "Default")
                settings.set_property(
                    "gtk-application-prefer-dark-theme",
                    True,
                )
            except Exception:
                pass

        if widget and isinstance(widget, Gtk.Dialog):
            return

    def load_default_css(self) -> None:
        provider = Gtk.CssProvider()
        provider.load_from_path(Const.STYLESHEET_DEFAULT_GTK.as_posix())

        screen = Gdk.Screen.get_default()  # type: ignore
        if screen:
            Gtk.StyleContext.add_provider_for_screen(  # type: ignore
                screen,
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
