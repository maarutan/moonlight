from pathlib import Path
from utils import JsonManager
from utils import FileManager


class ConfigHandler:
    def __init__(
        self,
        config_dir: Path | str,
        config_file: Path | str,
        default_config: str,
    ) -> None:
        self.jsonc = JsonManager()
        self.fm = FileManager()
        self.fm.if_not_exists_create(Path(config_dir))
        self.path = Path(config_file)
        self.cfg = default_config

        self.generate_default_config()

    # Config

    def generate_default_config(self) -> None:
        if self.fm.read(self.path) in [None, ""]:
            self.fm.write(self.path, self.cfg)  # type: ignore

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
