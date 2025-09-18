from pathlib import Path
from utils import ConfigHandler
from ._prep_cfg import CavaCfg, ConfParser


class ConfigHandlerCavalade(ConfigHandler):
    def __init__(
        self,
        name: str,
        dir: Path | str,
        file: Path | str,
    ):
        super().__init__(
            config_dir=dir,
            config_file=file,
        )
        self.cava = CavaCfg(self)

        self.cava.general()
        self.cava.output()
        self.cava.smoothing()
        self.cava.equalizer()

        self.config_file = ConfParser(
            config_name=name,  # pyright: ignore[reportCallIssue]]
            config_file=file,
        ).local_config_file
