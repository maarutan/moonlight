import os
from typing import TYPE_CHECKING
from config import ASSETS

if TYPE_CHECKING:
    from .._config_handler import ConfigHandler


class MediaPlayerWindowsTitleCfg:
    def __init__(self, _cfg: "ConfigHandler") -> None:
        self._cfg = _cfg
        self.parent = "media-player-with-windows-title"

    def if_empty_ghost_will_come_out(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(
            self.parent, "if-empty-ghost-will-come-out", default=dflt
        )
        return i if isinstance(i, bool) else dflt

    def ghost_size(self) -> int:
        dflt = 400
        i = self._cfg._get_nested(self.parent, "ghost-size", default=dflt)
        return i if isinstance(i, int) else dflt

    def single_active_player(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "single-active-player", default=dflt)
        return i if isinstance(i, bool) else dflt

    def background_path(self) -> str:
        dflt = ""
        i = self._cfg._get_nested(self.parent, "background-path", default=dflt)
        if not isinstance(i, str):
            return dflt

        if i.startswith("{assets}"):
            return i.format(assets=ASSETS)
        elif i.startswith("~"):
            return os.path.expanduser(i)
        else:
            return i
