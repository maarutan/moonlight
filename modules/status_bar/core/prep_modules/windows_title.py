from ...modules.title_window.windows_title import WindowsTitle
from .._config_handler import ConfigHandlerStatusBar


def windows_title_handler(cfg: ConfigHandlerStatusBar) -> WindowsTitle:
    return WindowsTitle(
        truncation=cfg.windows_title.truncation(),
        truncation_size=cfg.windows_title.truncation_size(),
        title_map=cfg.windows_title.map(),
        vertical_title_length=cfg.windows_title.vertical_title_length(),
        enable_icon=cfg.windows_title.enable_icon(),
        is_horizontal=cfg.bar.is_horizontal(),
        title_exceptions=cfg.windows_title.exceptions(),
        resolve_icon=cfg.windows_title.icon_resolve()["enable"],
        resolve_icon_size=cfg.windows_title.icon_resolve()["size"],
        resolve_position=cfg.windows_title.icon_resolve()["position"],
        title_type=cfg.windows_title.title_type()["type"],
        title_type_length=cfg.windows_title.title_type()["length"],
    )
