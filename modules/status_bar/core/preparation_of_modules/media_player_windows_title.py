from ...modules.title_window.media_player_with_windows_title import MPWitWindowsTitle
from .._config_handler import ConfigHandler
from .windows_title import windows_title_handler


def mp_windows_title_handler(conf: ConfigHandler) -> MPWitWindowsTitle:
    return MPWitWindowsTitle(
        windows_title_handler(conf),
        orientation_pos=conf.is_horizontal(),
    )
