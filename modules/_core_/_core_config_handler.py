from ._default_config import Configuration
from utils import ConfigHandler
from config import (
    APP_CONFIG_DIR,
    APP_CONFIG_FILE,
)
from ._prep_cfg import (
    ScreenCornersCfg,
    ActivateLinuxCfg,
    StatusBarCfg,
    BatteryAlertCfg,
    LanguagePreviewCfg,
    DesktopClockCfg,
    DockStationCfg,
)


class CoreConfigHandler(ConfigHandler):
    def __init__(self):
        super().__init__(
            config_dir=APP_CONFIG_DIR,
            config_file=APP_CONFIG_FILE,
            default_config=Configuration.DEFAULT.value,  # type:ignore
        )
        self.screen_corners = ScreenCornersCfg(self)
        self.activate_linux = ActivateLinuxCfg(self)
        self.status_bar = StatusBarCfg(self)
        self.battery_alert = BatteryAlertCfg(self)
        self.language_preview = LanguagePreviewCfg(self)
        self.desktop_clock = DesktopClockCfg(self)
        self.dock_station = DockStationCfg(self)
