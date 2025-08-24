from ...modules.title_window.windows_title import WindowsTitle
from .._config_handler import ConfigHandler


def windows_title_handler(cfg: ConfigHandler) -> WindowsTitle:
    return WindowsTitle(
        truncation=cfg.windows_title.truncation(),
        truncation_size=cfg.windows_title.truncation_size(),
        title_map=cfg.windows_title.map(),
        vertical_title_length=cfg.windows_title.vertical_title_length(),
        enable_icon=cfg.windows_title.enable_icon(),
        is_horizontal=cfg.bar.is_horizontal(),
        title_exceptions=cfg.windows_title.exceptions(),
        icon_resolve=cfg.windows_title.icon_resolve()["enable"],
        icon_size=cfg.windows_title.icon_resolve()["size"],
    )
