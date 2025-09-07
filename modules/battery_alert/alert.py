import logging
import shlex
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
        GLib.idle_add(self.set_update)
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
                "charging-popup-progressbar-low",
                "charging-popup-progressbar-medium",
                "charging-popup-progressbar-high",
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

    def set_update(self):
        try:
            state_code = int(self.battery.get_property("State") or 0)
        except Exception:
            state_code = 0
        current_state = DeviceState.get(state_code, "UNKNOWN")
        curr_is_charging = current_state == "CHARGING"
        key = f"{self.base_lock_parent_name}.is_charging"
        prev = self.json.get_with_dot_data(BASE_LOCK, key)

        if prev is None:
            self.json.update(BASE_LOCK, key, curr_is_charging)
            logging.debug("ChargingPopup: first run — saved state, no sound.")
            return

        if isinstance(prev, bool):
            prev_bool = prev
        else:
            prev_bool = str(prev).lower() in ("1", "true", "yes")

        try:
            pct = float(
                self.battery.get_property("Percentage") or self.current_percentage
            )
            self.current_percentage = pct
        except Exception:
            pass

        try:
            self.progress_bar.set_value(self.current_percentage)
        except Exception:
            logging.exception("ChargingPopup: failed to update progress value")

        if prev_bool != curr_is_charging:
            if not prev_bool and curr_is_charging:
                logging.info(
                    "ChargingPopup: detected connect -> playing charging sound"
                )
                exec_shell_command_async(
                    f"mpv --volume-gain=30 {self._quote_path(CHARGING_SOUND)}"
                )
                self.toggle_popup("show")
                self._start_hide_timer(seconds=self.hide_timeout)
            elif prev_bool and not curr_is_charging:
                logging.info(
                    "ChargingPopup: detected disconnect -> playing disconnect sound"
                )
                exec_shell_command_async(
                    f"mpv --volume-gain=30 {self._quote_path(DISCONNECT_CHARGING_SOUND)}"
                )
                self._start_hide_timer(seconds=self.hide_timeout)

        level = None
        try:
            pct_rounded = round(self.current_percentage)
            if not curr_is_charging:
                if pct_rounded >= self.alert_progress["high"]:
                    level = "high"
                elif pct_rounded >= self.alert_progress["medium"]:
                    level = "medium"
                elif pct_rounded >= self.alert_progress["low"]:
                    level = "low"
        except Exception:
            level = None

        if level is not None and level != self.last_alert:
            self._clear_alert_classes()
            try:
                self.progress_bar.add_style_class(
                    f"charging-popup-progress-bar-{level}"
                )
            except Exception:
                pass
            try:
                self.popup_box.add_style_class(f"charging-popup-box-{level}")
            except Exception:
                pass
            self._ensure_icon_child()
            if level == "low":
                self.progress_bar_icon.set_label(self.low_icon)
                self._start_hide_timer(self.hide_timeout)
            elif level == "medium":
                self.progress_bar_icon.set_label(self.medium_icon)
                self._start_hide_timer(self.hide_timeout)
            elif level == "high":
                self.progress_bar_icon.set_label(self.high_icon)
                self._start_hide_timer(self.hide_timeout)
            self.toggle_popup("show")
            self.last_alert = level
        elif level is None:
            if self.last_alert is not None:
                self._clear_alert_classes()
                self._ensure_icon_child()
                self.progress_bar_icon.set_label(self.charging_icon)
                self.last_alert = None

        self.json.update(BASE_LOCK, key, curr_is_charging)
