from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class ModulesCfg:
    def __init__(self, cfg_handler: "ConfigHandlerStatusBar") -> None:
        self._cfg = cfg_handler

    def get_modules_start(self) -> list[str]:
        i = self._cfg._get_options("modules-start", [])
        return i if isinstance(i, list) else []

    def get_modules_center(self) -> list[str]:
        i = self._cfg._get_options("modules-center", [])
        return i if isinstance(i, list) else []

    def get_modules_end(self) -> list[str]:
        i = self._cfg._get_options("modules-end", [])
        return i if isinstance(i, list) else []
