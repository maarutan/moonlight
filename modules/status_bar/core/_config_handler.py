from ..cfg.default_config import Configuration
from utils import ConfigHandler
from .prep_cfg import (
    StatusBarCfg,
    WorkspacesCfg,
    ProfileCfg,
    ModulesCfg,
    SystemTrayCfg,
    MemoryRamCfg,
    MetricsCfg,
    WindowsTitleCfg,
    LanguageCfg,
    ScreenRecorderCfg,
    ClockCfg,
    MediaPlayerWindowsTitleCfg,
    BatteryCfg,
)
from config import (
    STATUS_BAR_DIR,
    STATUS_BAR_CONFIG,
)


class ConfigHandlerStatusBar(ConfigHandler):
    def __init__(self) -> None:
        super().__init__(
            config_dir=STATUS_BAR_DIR,
            config_file=STATUS_BAR_CONFIG,
            default_config=Configuration.DEFAULT.value,
        )
        self.bar = StatusBarCfg(self)
        self.workspaces = WorkspacesCfg(self)
        self.profile = ProfileCfg(self)
        self.modules = ModulesCfg(self)
        self.system_tray = SystemTrayCfg(self)
        self.memory_ram = MemoryRamCfg(self)
        self.windows_title = WindowsTitleCfg(self)
        self.language = LanguageCfg(self)
        self.clock = ClockCfg(self)
        self.media_player_windows_title = MediaPlayerWindowsTitleCfg(self)
        self.metrics = MetricsCfg(self)
        self.screen_recorder = ScreenRecorderCfg(self)
        self.battery = BatteryCfg(self)
