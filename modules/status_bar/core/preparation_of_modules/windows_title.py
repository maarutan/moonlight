from ...modules.title_window.windows_title import WindowsTitle
from .._config_handler import ConfigHandler


def windows_title_handler(conf: ConfigHandler) -> WindowsTitle:
    return WindowsTitle(
        truncation=conf.get_truncation_title(),
        truncation_size=conf.get_truncation_size_title(),
        title_map=conf.get_title_map(),
        vertical_title_length=conf.get_vertical_title_length(),
        enable_icon=conf.get_enable_icon(),
        orientation_pos=conf.is_horizontal(),
    )
