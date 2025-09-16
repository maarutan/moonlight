from ._core_config_handler import CoreConfigHandler
from fabric import Application
from config import APP_NAME, MAIN_CSS_FILE

from ._prep_modules import (
    screen_corners_handler,
    activate_linux_handler,
    ScreenMenu,
    status_bar_handler,
    battery_alert_handler,
    language_preview_handler,
    desktop_clock_handler,
    dock_station_handler,
)


class ModulesHandler:
    def __init__(self) -> None:
        self.cfg = CoreConfigHandler()
        self.Application = self.app()

    def app(self) -> Application:
        return Application(
            f"{APP_NAME}",
            screen_corners_handler(self.cfg),
            activate_linux_handler(self.cfg),
            status_bar_handler(self.cfg),
            battery_alert_handler(self.cfg),
            language_preview_handler(self.cfg),
            desktop_clock_handler(self.cfg),
            dock_station_handler(self.cfg),
            # ScreenMenu(),
        )

    def set_css(self) -> None:
        return self.Application.set_stylesheet_from_file(MAIN_CSS_FILE.as_posix())
