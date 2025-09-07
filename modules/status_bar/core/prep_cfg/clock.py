from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class ClockCfg:
    def __init__(self, cfg_handler: "ConfigHandlerStatusBar") -> None:
        self._cfg = cfg_handler
        self.parent = "clock"

    def get_clock(self) -> int:
        i = self._cfg._get_options(self.parent, 12)

        if isinstance(i, int):
            return i
        if isinstance(i, str) and i.isdigit():
            return int(i)

        return 12  # fallback
