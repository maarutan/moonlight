from ...modules.title_window.media_player_with_windows_title import MPWitWindowsTitle
from .._config_handler import ConfigHandler
from .windows_title import windows_title_handler


def mp_windows_title_handler(cfg: ConfigHandler) -> MPWitWindowsTitle:
    return MPWitWindowsTitle(
        windows_title_handler(cfg),
        is_horizontal=cfg.bar.is_horizontal(),
        ghost_size=cfg.media_player_windows_title.ghost_size(),
        single_active_player=cfg.media_player_windows_title.single_active_player(),
        if_empty_ghost_will_come_out=cfg.media_player_windows_title.if_empty_ghost_will_come_out(),
        background_path=cfg.media_player_windows_title.background_path(),
    )
