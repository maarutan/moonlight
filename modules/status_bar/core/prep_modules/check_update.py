from ...modules.check_update.check import CheckUpdate
from .._config_handler import ConfigHandlerStatusBar


def check_update_handler(cfg: ConfigHandlerStatusBar) -> CheckUpdate:
    return CheckUpdate(
        is_horizontal=cfg.bar.is_horizontal(),
        pkg_manager=cfg.check_update.pkg_manager(),
        on_clicked=cfg.check_update.on_clicked(),
        icon_position=cfg.check_update.icon_position(),
        interval=cfg.check_update.interval(),
    )
