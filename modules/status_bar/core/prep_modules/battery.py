from ...modules.battery.battery import Battery
from .._config_handler import ConfigHandler


def battery_handler(cfg: ConfigHandler) -> Battery:
    return Battery(
        is_horizontal=cfg.bar.is_horizontal(),
        percentage_enable=cfg.battery.percentage()["enable"],
        percentage_action_type=cfg.battery.percentage()["action-type"],
        percentage_position=cfg.battery.percentage()["position"],
        icon_enable=cfg.battery.icons()["enable"],
        icons_type=cfg.battery.icons()["type"],
        if_icon_not_found=cfg.battery.icons()["if-not-found"],
        custom_icons_file_path=cfg.battery.icons()["custom_icons_file_path"],
        custom_icons=cfg.battery.icons()["custom-icons"],
    )
