from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class CheckUpdateCfg:
    def __init__(self, cfg_handler: "ConfigHandlerStatusBar") -> None:
        self._cfg = cfg_handler
        self.parent = "check-update"

    def pkg_manager(self) -> str:
        dflt = "pacman"
        i = self._cfg._get_nested(self.parent, "pkg-manager", default=dflt)
        return i if isinstance(i, str) else dflt

    def on_clicked(self) -> str:
        dflt = "notify-send 'Empty (statusbar - check-update)'"
        i = self._cfg._get_nested(self.parent, "on-clicked", default=dflt)
        return i if isinstance(i, str) else dflt

    def icon_position(self) -> str:
        dflt = "left"
        i = self._cfg._get_nested(self.parent, "icon-position", default=dflt)
        return i if isinstance(i, str) else dflt

    def interval(self) -> int:
        dflt = 1
        i = self._cfg._get_nested(self.parent, "interval", default=dflt)
        return i if isinstance(i, int) else dflt
