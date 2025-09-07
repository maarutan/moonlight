from ...modules.system_tray.system_tray import SystemTrayHandler
from .._config_handler import ConfigHandlerStatusBar


def system_tray_handler(cfg: ConfigHandlerStatusBar) -> SystemTrayHandler:
    return SystemTrayHandler(
        tray_box_position=cfg.system_tray.box_position_handler(),
        orientation_pos=cfg.bar.is_horizontal(),
        bar_position=cfg.system_tray.position_for_tray_box(),
        pixel_size=cfg.system_tray.icon_size(),
        refresh_interval=cfg.system_tray.refresh_interval(),
        spacing=cfg.system_tray.spacing(),
        tray_box=cfg.system_tray.tray_box(),
    )
