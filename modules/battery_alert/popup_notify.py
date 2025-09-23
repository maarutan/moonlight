import logging
from typing import Optional, Literal
from gi.repository import GLib  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.centerbox import CenterBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .alert import BatteryAlert


class BatteryPopup(Window):
    def __init__(
        self,
        alert: "BatteryAlert",
        low_icon: str = "⚠",
        medium_icon: str = "⚠",
        high_icon: str = "!",
        charging_icon: str = "󱐋",
        hide_timeout: int = 3,
    ):
        super().__init__(
            name="battery-alert",
            anchor="top right",
            exclusivity="normal",
            layer="top",
            size=400,
        )
        self.alert = alert
        self.low_icon = low_icon
        self.medium_icon = medium_icon
        self.high_icon = high_icon
        self.charging_icon = charging_icon
        self.hide_timeout = hide_timeout
        self._hide_timeout_id: Optional[int] = None
        self.is_popup_show = False

        # === UI ===
        self.popup_box = Box(name="battery-alert-popup-box")
        self.progress_bar_icon = Label(
            name="battery-alert-progress-bar-icon", label=self.charging_icon
        )
        self.progress_bar = CircularProgressBar(
            name="battery-alert-progress-bar",
            value=0.0,
            size=124,
            line_width=24,
            start_angle=0,
            end_angle=360,
            max_value=100.0,
            child=self.progress_bar_icon,
        )
        self.battery_percentage_label = Label(
            name="battery-alert-percentage-label", label=f"{round(self.alert.pct)}%"
        )
        self.popup_box.add(
            CenterBox(
                start_children=self.progress_bar,
                end_children=self.battery_percentage_label,
            )
        )
        self.add(self.popup_box)
        GLib.timeout_add_seconds(1, lambda *_: (self.toggle_popup("hide"), False)[1])

    # === Popup logic ===
    def update_progress(self, pct: float):
        try:
            self.progress_bar.set_value(pct)
        except Exception:
            logging.exception("BatteryPopup: failed to update progress value")

    def toggle_popup(self, action: Literal["show", "hide"] = "show"):
        show = "battery-alert-popup-box-show"
        hide = "battery-alert-popup-box-hide"
        self.popup_box.remove_style_class(show)
        self.popup_box.remove_style_class(hide)
        if action == "show":
            self.show_all()
            self.progress_bar.show_all()
            self.battery_percentage_label.show_all()
            self.popup_box.add_style_class(show)
            self.is_popup_show = True
            return
        self.popup_box.add_style_class(hide)
        self.is_popup_show = False

    def show_popup(self, level: str, icon: str):
        self._clear_alert_classes()
        self.progress_bar_icon.set_label(icon)
        self._apply_level_classes(level)
        self._ensure_icon_child()
        self.toggle_popup("show")
        self._start_hide_timer(self.hide_timeout)

    def hide(self):
        self.toggle_popup("hide")

    # === Timer ===
    def _cancel_hide_timer(self):
        if self._hide_timeout_id:
            try:
                GLib.source_remove(self._hide_timeout_id)
            except Exception:
                logging.exception("BatteryPopup: failed to remove hide timeout")
            finally:
                self._hide_timeout_id = None

    def _on_hide_timeout(self) -> bool:
        try:
            self.hide()
        except Exception:
            logging.exception("BatteryPopup: error hiding popup")
        self._hide_timeout_id = None
        return False

    def _start_hide_timer(self, seconds: int):
        self._cancel_hide_timer()
        try:
            tid = GLib.timeout_add_seconds(int(seconds), self._on_hide_timeout)
            self._hide_timeout_id = int(tid)
        except Exception:
            logging.exception("BatteryPopup: failed to start hide timer")
            self._hide_timeout_id = None

    # === CSS helpers ===
    def _clear_alert_classes(self):
        classes = (
            "battery-alert-progress-bar-low",
            "battery-alert-progress-bar-medium",
            "battery-alert-progress-bar-high",
            "charging-popup-progress-bar-low",
            "charging-popup-progress-bar-medium",
            "charging-popup-progress-bar-high",
            "battery-alert-popup-box-low",
            "battery-alert-popup-box-medium",
            "battery-alert-popup-box-high",
            "charging-popup-box-low",
            "charging-popup-box-medium",
            "charging-popup-box-high",
        )
        for cls in classes:
            try:
                self.progress_bar.remove_style_class(cls)
            except Exception:
                pass
            try:
                self.popup_box.remove_style_class(cls)
            except Exception:
                pass

    def _apply_level_classes(self, level: str):
        try:
            self.progress_bar.add_style_class(f"battery-alert-progress-bar-{level}")
            self.progress_bar.add_style_class(f"charging-popup-progress-bar-{level}")
            self.popup_box.add_style_class(f"battery-alert-popup-box-{level}")
            self.popup_box.add_style_class(f"charging-popup-box-{level}")
        except Exception:
            pass

    def _ensure_icon_child(self):
        try:
            if hasattr(self.progress_bar, "children"):
                if self.progress_bar_icon not in self.progress_bar.children:
                    self.progress_bar.add(self.progress_bar_icon)
        except Exception:
            pass
