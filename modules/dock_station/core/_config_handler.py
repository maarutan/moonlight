from ..cfg.default_config import Configuration
from utils import ConfigHandler
from config import DOCK_STATION_DIR, DOCK_STATION_CONFIG

from .prep_cfg import (
    DockCfg,
    PinsCfg,
)


class ConfigHandlerDockStation(ConfigHandler):
    def __init__(self):
        super().__init__(
            config_dir=DOCK_STATION_DIR,
            config_file=DOCK_STATION_CONFIG,
            default_config=Configuration.DEFAULT.value,  # type:ignore
        )
        PinsCfg()
        self.dock = DockCfg(self)
