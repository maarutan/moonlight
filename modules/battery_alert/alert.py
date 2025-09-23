import logging
import shlex
import time
from gi.repository import GLib  # type: ignore

from config.data import DISCONNECT_CHARGING_SOUND
from config import CHARGING_SOUND, BASE_LOCK
from services import BatteryService, DeviceState
from fabric.utils import exec_shell_command_async
from utils import JsonManager
from .popup_notify import BatteryPopup
from utils import setup_cursor_hover


class BatteryAlert:
    def __init__(
        self,
        enabled: bool = True,
        low_icon: str = "⚠",
        medium_icon: str = "⚠",
        high_icon: str = "!",
        charging_icon: str = "󱐋",
        hide_timeout: int = 3,
        alert_progress: dict | None = None,
        alert_cooldown: int = 300,
    ):
        self.battery = BatteryService()
        self.json = JsonManager()

        try:
            self.pct: float = float(self.battery.get_property("Percentage") or 0.0)
        except Exception:
            self.pct = 0.0

        self.alert_progress = alert_progress or {"low": 5, "medium": 20, "high": 80}
        self.alert_cooldown = alert_cooldown
        self.last_alert: str | None = None
        self.last_alert_time: float = 0.0
        self.base_lock_parent_name = "battery-alert"

        self.popup = BatteryPopup(
            alert=self,
            low_icon=low_icon,
            medium_icon=medium_icon,
            high_icon=high_icon,
            charging_icon=charging_icon,
            hide_timeout=hide_timeout,
        )
        self.popup.connect(
            "button-press-event", lambda *_: self.popup.toggle_popup("hide")
        )
        setup_cursor_hover(self.popup)

        if enabled:
            GLib.idle_add(self.set_update)
            GLib.timeout_add_seconds(15, self._poll_update)
            self.battery.changed.connect(self._on_battery_changed)

    def _quote_path(self, p):
        return shlex.quote(p.as_posix() if hasattr(p, "as_posix") else str(p))

    def _can_alert(self, level: str) -> bool:
        now = time.time()
        if (
            self.last_alert == level
            and (now - self.last_alert_time) < self.alert_cooldown
        ):
            return False
        self.last_alert = level
        self.last_alert_time = now
        return True

    def _on_battery_changed(self, *args) -> bool:
        GLib.idle_add(self.set_update)
        return False

    def _poll_update(self):
        try:
            self.set_update()
        except Exception:
            logging.exception("Polling update failed")
        return True

    def set_update(self):
        # === State ===
        try:
            state_code = int(self.battery.get_property("State") or 0)
        except Exception:
            state_code = 0
        current_state = DeviceState.get(state_code, "UNKNOWN")
        curr_is_charging = current_state == "CHARGING"

        # === Prev state from json ===
        key = f"{self.base_lock_parent_name}.is_charging"
        prev = self.json.get_with_dot_data(BASE_LOCK, key)
        if prev is None:
            prev_bool = curr_is_charging
            self.json.update(BASE_LOCK, key, curr_is_charging)
        else:
            prev_bool = (
                bool(prev)
                if isinstance(prev, bool)
                else str(prev).lower() in ("1", "true", "yes")
            )

        # === Percentage ===
        try:
            self.pct = float(self.battery.get_property("Percentage") or 0.0)
        except Exception:
            self.pct = 0.0

        self.popup.update_progress(self.pct)
        self.popup.battery_percentage_label.set_text(f"{round(self.pct)}%")

        # === Charging events ===
        if prev_bool != curr_is_charging:
            if not prev_bool and curr_is_charging:
                if self._can_alert("charging"):
                    exec_shell_command_async(
                        f"mpv --no-terminal --really-quiet --volume-gain=30 {self._quote_path(CHARGING_SOUND)}"
                    )
                    self.popup.show_popup("charging", self.popup.charging_icon)
            elif prev_bool and not curr_is_charging:
                if self._can_alert("disconnect"):
                    exec_shell_command_async(
                        f"mpv --no-terminal --really-quiet --volume-gain=30 {self._quote_path(DISCONNECT_CHARGING_SOUND)}"
                    )
                    self.popup.show_popup("disconnect", self.popup.low_icon)

        # === Thresholds ===
        pct_rounded = round(self.pct)
        matched_level = None
        for lvl, thresh in self.alert_progress.items():
            try:
                if int(round(float(thresh))) == pct_rounded:
                    matched_level = lvl
                    break
            except Exception:
                continue

        # === Range-based ===
        range_level = None
        if not curr_is_charging:
            if pct_rounded >= int(round(float(self.alert_progress.get("high", 100)))):
                range_level = "high"
            elif pct_rounded >= int(round(float(self.alert_progress.get("medium", 0)))):
                range_level = "medium"
            elif pct_rounded >= int(round(float(self.alert_progress.get("low", 0)))):
                range_level = "low"

        # === Alerts ===
        icon_map = {
            "low": self.popup.low_icon,
            "medium": self.popup.medium_icon,
            "high": self.popup.high_icon,
        }

        if matched_level and self._can_alert(
            f"pct_{self.alert_progress[matched_level]}"
        ):
            self.popup.show_popup(matched_level, icon_map.get(matched_level, "⚠"))
        elif range_level and self._can_alert(range_level):
            self.popup.show_popup(range_level, icon_map.get(range_level, "⚠"))

        # === Save state ===
        self.json.update(BASE_LOCK, key, curr_is_charging)
