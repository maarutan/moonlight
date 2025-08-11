from ..cfg.default_config import Configuration
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
    ClockCfg,
    MediaPlayerWindowsTitleCfg,
)
from config import (
    STATUS_BAR_DIR,
    STATUS_BAR_CONFIG,
)

from pathlib import Path
from utils import JsonManager
from utils import FileManager


class ConfigHandler:
    def __init__(self) -> None:
        self.jsonc = JsonManager()
        self.fm = FileManager()
        self.fm.if_not_exists_create(STATUS_BAR_DIR)
        self.path = Path(STATUS_BAR_CONFIG)
        self.cfg = Configuration

        self.generate_default_config()

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

    # Config

    def generate_default_config(self) -> None:
        if self.fm.read(self.path) in [None, ""]:
            self.fm.write(self.path, self.cfg.DEFAULT.value)

    # Options

    def _get_options(
        self,
        key: str,
        default: str | int | bool | dict | list | None = None,
    ) -> str | int | bool | dict | list | None:
        data = self.jsonc.read(self.path)
        return data.get(key, default) if data else default

    def _get_nested(self, *keys, default=None):
        data = self._get_options(keys[0], {})
        for key in keys[1:]:
            if not isinstance(data, dict):
                return default
            data = data.get(key, default)
        return data
