from ...modules.network_speed import NetworkSpeed
from .._config_handler import ConfigHandlerStatusBar


def network_speed_handler(cfg: ConfigHandlerStatusBar) -> NetworkSpeed:
    return NetworkSpeed(
        is_horizontal=cfg.bar.is_horizontal(),
        speed_type=cfg.network_speed.speed_type(),
        icon_position=cfg.network_speed.icons()["position"],
        icon_download=cfg.network_speed.icons()["download"],
        if_one_icon=cfg.network_speed.icons()["if_one"],
        icon_upload=cfg.network_speed.icons()["upload"],
        interval=cfg.network_speed.interval(),
    )
