import logging
import shlex
import time
from typing import Literal, Optional
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.circularprogressbar import CircularProgressBar
from gi.repository import GLib  # type: ignore
from config.data import DISCONNECT_CHARGING_SOUND
from services import BatteryService, DeviceState
from fabric.utils import exec_shell_command_async
from config import CHARGING_SOUND, BASE_LOCK
from utils import JsonManager


class BatteryAlert(Window):
    def __init__(
        self,
        enabled: bool = True,
        low_icon: str = "⚠",
        medium_icon: str = "⚠",
        high_icon: str = "!",
        charging_icon: str = "󱐋",
        hide_timeout: int = 3,
        alert_progress: dict = {
            "low": 5,
            "medium": 20,
            "high": 80,
        },
    ) -> None:
        super().__init__(
            name="battery-alert",
            anchor="top right",
            exclusivity="normal",
            layer="top",
            size=400,
        )
        self.charging_icon = charging_icon
        self.low_icon = low_icon
        self.medium_icon = medium_icon
        self.high_icon = high_icon
        self.hide_timeout = hide_timeout
        self.alert_progress = alert_progress
        self.json = JsonManager()
        self.base_lock_parent_name = "battery-alert"
        self._hide_timeout_id: Optional[int] = None
        self.battery = BatteryService()
        self.current_percentage = float(self.battery.get_property("Percentage") or 0.0)
        # self.current_percentage = 90.0
        self.popup_box = Box(name="battery-alert-popup-box")
        self.progress_bar_icon = Label(
            name="battery-alert-progress-bar-icon", label=self.charging_icon
        )
        self.progress_bar = CircularProgressBar(
            name="battery-alert-progress-bar",
            value=self.current_percentage,
            size=124,
            line_width=24,
            start_angle=0,
            end_angle=360,
            max_value=100.00,
            child=self.progress_bar_icon,
        )
        self.popup_box.add(self.progress_bar)
        self.toggle_popup("hide")
        self.add(self.popup_box)
        self.is_popup_show = False
        try:
            self.battery_state = self.battery.get_property("State")
        except Exception:
            self.battery_state = None
        self.device_state = DeviceState.get(int(self.battery_state or 0), "UNKNOWN")
        self.last_alert: Optional[str] = None
        self.last_alert_time = 0.0
        self.alert_cooldown = 300

        if enabled:
            GLib.idle_add(self.set_update)
            GLib.timeout_add_seconds(15, self._poll_update)
            self.battery.changed.connect(self._on_battery_changed)

    def _quote_path(self, p):
        return shlex.quote(p.as_posix() if hasattr(p, "as_posix") else str(p))

    def _on_battery_changed(self, *args) -> bool:
        GLib.idle_add(self.set_update)
        return False

    def _cancel_hide_timer(self) -> None:
        if self._hide_timeout_id:
            try:
                GLib.source_remove(self._hide_timeout_id)
            except Exception:
                logging.exception(
                    "ChargingPopup: failed to remove existing hide timeout"
                )
            finally:
                self._hide_timeout_id = None

    def _on_hide_timeout(self) -> bool:
        try:
            self.toggle_popup("hide")
        except Exception:
            logging.exception("ChargingPopup: error while hiding popup from timeout")
        self._hide_timeout_id = None
        return False

    def _start_hide_timer(self, seconds: int = 4) -> None:
        self._cancel_hide_timer()
        try:
            tid = GLib.timeout_add_seconds(int(seconds), self._on_hide_timeout)
            self._hide_timeout_id = int(tid)
        except Exception:
            logging.exception("ChargingPopup: failed to start hide timer")
            self._hide_timeout_id = None

    def toggle_popup(self, action: Literal["show", "hide"] = "show"):
        show = "battery-alert-popup-box-show"
        hide = "battery-alert-popup-box-hide"
        self.popup_box.remove_style_class(show)
        self.popup_box.remove_style_class(hide)
        if action == "show":
            self.popup_box.add_style_class(show)
            self.is_popup_show = True
            return
        self.popup_box.add_style_class(hide)
        self.is_popup_show = False

    def _ensure_icon_child(self):
        try:
            if hasattr(self.progress_bar, "children"):
                if self.progress_bar_icon not in self.progress_bar.children:
                    self.progress_bar.add(self.progress_bar_icon)
        except Exception:
            pass

    def _clear_alert_classes(self):
        try:
            for cls in (
                "battery-alert-progress-bar-low",
                "battery-alert-progress-bar-medium",
                "battery-alert-progress-bar-high",
                "charging-popup-progress-bar-low",
                "charging-popup-progress-bar-medium",
                "charging-popup-progress-bar-high",
                "charging-popup-progressbar-low",
                "charging-popup-progressbar-medium",
                "charging-popup-progressbar-high",
                "battery-alert-popup-box-low",
                "battery-alert-popup-box-medium",
                "battery-alert-popup-box-high",
                "charging-popup-box-low",
                "charging-popup-box-medium",
                "charging-popup-box-high",
            ):
                try:
                    self.progress_bar.remove_style_class(cls)
                except Exception:
                    pass
                try:
                    self.popup_box.remove_style_class(cls)
                except Exception:
                    pass
        except Exception:
            pass

    def _poll_update(self):
        try:
            self.set_update()
        except Exception:
            logging.exception("Polling update failed")
        return True

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

    def set_update(self):
        try:
            state_code = int(self.battery.get_property("State") or 0)
        except Exception:
            state_code = 0
        current_state = DeviceState.get(state_code, "UNKNOWN")
        curr_is_charging = current_state == "CHARGING"
        key = f"{self.base_lock_parent_name}.is_charging"
        prev = self.json.get_with_dot_data(BASE_LOCK, key)
        first_run = False
        if prev is None:
            first_run = True
            self.json.update(BASE_LOCK, key, curr_is_charging)
            prev_bool = curr_is_charging
        else:
            if isinstance(prev, bool):
                prev_bool = prev
            else:
                prev_bool = str(prev).lower() in ("1", "true", "yes")
        try:
            # pct = float(self.battery.get_property("Percentage") or self.current_percentage)
            pct = self.fake_percentage
            self.current_percentage = pct
        except Exception:
            pass
        try:
            self.progress_bar.set_value(self.current_percentage)
        except Exception:
            logging.exception("ChargingPopup: failed to update progress value")
        if prev_bool != curr_is_charging and not first_run:
            if not prev_bool and curr_is_charging:
                if self._can_alert("charging"):
                    exec_shell_command_async(
                        f"mpv --volume-gain=30 {self._quote_path(CHARGING_SOUND)}"
                    )
                    self.toggle_popup("show")
                    self._start_hide_timer(seconds=self.hide_timeout)
            elif prev_bool and not curr_is_charging:
                if self._can_alert("disconnect"):
                    exec_shell_command_async(
                        f"mpv --volume-gain=30 {self._quote_path(DISCONNECT_CHARGING_SOUND)}"
                    )
                    self._start_hide_timer(seconds=self.hide_timeout)
        pct_rounded = None
        try:
            pct_rounded = round(self.current_percentage)
        except Exception:
            pct_rounded = None
        matched_level = None
        matched_threshold = None
        try:
            if pct_rounded is not None:
                for lvl, thresh in self.alert_progress.items():
                    try:
                        if int(round(float(thresh))) == int(pct_rounded):
                            matched_level = lvl
                            matched_threshold = int(round(float(thresh)))
                            break
                    except Exception:
                        continue
        except Exception:
            matched_level = None
            matched_threshold = None
        range_level = None
        try:
            if pct_rounded is not None and not curr_is_charging:
                if pct_rounded >= int(
                    round(float(self.alert_progress.get("high", 100)))
                ):
                    range_level = "high"
                elif pct_rounded >= int(
                    round(float(self.alert_progress.get("medium", 0)))
                ):
                    range_level = "medium"
                elif pct_rounded >= int(
                    round(float(self.alert_progress.get("low", 0)))
                ):
                    range_level = "low"
        except Exception:
            range_level = None
        if matched_level is not None and self._can_alert(f"pct_{matched_threshold}"):
            self._clear_alert_classes()
            self.progress_bar.add_style_class(
                f"battery-alert-progress-bar-{matched_level}"
            )
            self.progress_bar.add_style_class(
                f"charging-popup-progress-bar-{matched_level}"
            )
            self.popup_box.add_style_class(f"battery-alert-popup-box-{matched_level}")
            self.popup_box.add_style_class(f"charging-popup-box-{matched_level}")
            self._ensure_icon_child()
            if matched_level == "low":
                self.progress_bar_icon.set_label(self.low_icon)
                self.toggle_popup("show")
                self._start_hide_timer(self.hide_timeout)
            elif matched_level == "medium":
                self.progress_bar_icon.set_label(self.medium_icon)
                self.toggle_popup("show")
                self._start_hide_timer(self.hide_timeout)
            elif matched_level == "high":
                self.progress_bar_icon.set_label(self.high_icon)
                self.toggle_popup("show")
                self._start_hide_timer(self.hide_timeout)
        elif range_level is not None and self._can_alert(range_level):
            self._clear_alert_classes()
            self.progress_bar.add_style_class(
                f"battery-alert-progress-bar-{range_level}"
            )
            self.progress_bar.add_style_class(
                f"charging-popup-progress-bar-{range_level}"
            )
            self.popup_box.add_style_class(f"battery-alert-popup-box-{range_level}")
            self.popup_box.add_style_class(f"charging-popup-box-{range_level}")
            self._ensure_icon_child()
            if range_level == "low":
                self.progress_bar_icon.set_label(self.low_icon)
                self.toggle_popup("show")
                self._start_hide_timer(self.hide_timeout)
            elif range_level == "medium":
                self.progress_bar_icon.set_label(self.medium_icon)
                self.toggle_popup("show")
                self._start_hide_timer(self.hide_timeout)
            elif range_level == "high":
                self.progress_bar_icon.set_label(self.high_icon)
                self.toggle_popup("show")
                self._start_hide_timer(self.hide_timeout)
        self.json.update(BASE_LOCK, key, curr_is_charging)
