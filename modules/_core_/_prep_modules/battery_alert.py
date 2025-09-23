from typing import TYPE_CHECKING
from modules import BatteryAlert

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def battery_alert_handler(cfg: "CoreConfigHandler") -> BatteryAlert:
    return BatteryAlert(
        enabled=cfg.battery_alert.enabled(),
        low_icon=cfg.battery_alert.icons()["low"],
        medium_icon=cfg.battery_alert.icons()["medium"],
        high_icon=cfg.battery_alert.icons()["high"],
        hide_timeout=cfg.battery_alert.hide_timeout(),
        alert_progress=cfg.battery_alert.alert_progress(),
    ).popup
