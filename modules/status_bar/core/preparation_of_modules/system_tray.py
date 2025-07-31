from ...modules.system_tray.system_tray import SystemTrayHandler
from .._config_handler import ConfigHandler


def system_tray_handler(conf: ConfigHandler) -> SystemTrayHandler:
    return SystemTrayHandler(
        tray_box_position=conf.tray_box_position_handler(),
        orientation_pos=conf.is_horizontal(),
        bar_position=conf.get_bar_position_for_tray_box(),
        pixel_size=conf.get_tray_icon_size(),
        refresh_interval=conf.get_tray_refresh_interval(),
        spacing=conf.get_tray_spacing(),
        tray_box=conf.get_tray_box(),
    )
