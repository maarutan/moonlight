from loguru import logger
from gi.repository import GLib, Gdk  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from services.screen_record import get_screen_recorder
from utils import JsonManager, setup_cursor_hover
from config import STATUS_BAR_LOCK_MODULES
from fabric.widgets.button import Button


class ScreenRecorder(Box):
    def __init__(
        self,
        icons_enable: bool = True,
        first_icon: str = "󰄘",
        second_icon: str = "󰄙",
        stop_icon: str = "",
        blink: bool = True,
        blink_interval: int = 400,
        timer: bool = True,
        is_horizontal: bool = True,
    ):
        self.first_icon = first_icon
        self.second_icon = second_icon
        self.stop_icon = stop_icon
        self.blink = blink
        self.timer = timer
        self.json = JsonManager()
        self.is_horizontal = is_horizontal

        super().__init__(
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
            orientation="h" if self.is_horizontal else "v",
        )

        self.default_seconds = 0
        self.icons_enable = icons_enable
        self.icon_label = Label(
            name="statusbar-screen-recorder-icon",
            label=self.first_icon if self.icons_enable else "",
        )

        try:
            self.icon_label.get_style_context().add_class("screen-recorder-icon")
        except Exception:
            pass

        self.icon_button = Button(
            name="statusbar-screen-recorder-wrapper",
            v_align="center",
            h_align="center",
            v_expand=True,
            h_expand=True,
        )
        self.timer_label = Label(
            name="statusbar-screen-recorder-time",
            label="",
        )
        self.blink_interval = blink_interval
        self._icon_state = True

        self.child_box = Box(
            name="statusbar-screen-recorder-indicator",
        )
        self.child_box.add(self.icon_label)

        try:
            self.child_box.add_style_class("screen-recorder-indicator")
        except Exception:
            pass

        self.icon_button.add(self.child_box)
        self.child_wrapper = Box(
            name="statusbar-screen-recorder-child-wrapper",
            orientation="h" if self.is_horizontal else "v",
            v_align="center",
            h_align="center",
            v_expand=True,
            h_expand=True,
        )
        self.child_wrapper.add(self.icon_button)
        self.child_wrapper.add(self.timer_label)

        self.add(self.child_wrapper)
        setup_cursor_hover(self.icon_button, "pointer")
        self.icon_button.connect("enter-notify-event", self._enter_button)
        self.icon_button.connect("leave-notify-event", self._leave_button)
        self.icon_button.connect("button-press-event", self._press_button)

        try:
            self.set_no_show_all(True)
            self.child_box.set_no_show_all(True)
            self.timer_label.set_no_show_all(True)
        except Exception:
            pass

        self.child_box.hide()
        self.timer_label.hide()
        self.hide()

        self._seconds = self.default_seconds
        self._timer_id = None
        self._blink_id = None

        self.recorder_service = get_screen_recorder()
        self.recorder_service.recording.connect(self.on_recording_change)

        if self.is_horizontal:
            self.get_style_context().add_class("horizontal")
        else:
            self.get_style_context().add_class("vertical")

        try:
            self.is_background_recording = self.json.get_with_dot_data(
                STATUS_BAR_LOCK_MODULES, "screen_recorder.is_recording"
            )
            if self.is_background_recording:
                self.default_seconds = self.json.get_with_dot_data(
                    STATUS_BAR_LOCK_MODULES,
                    "screen_recorder.seconds",
                )
                self._seconds = self.default_seconds
                GLib.idle_add(self._start_timer)
            else:
                GLib.idle_add(self._stop_timer)
        except Exception:
            GLib.idle_add(self._stop_timer)

    def _enter_button(self, *event):
        self.blink = False
        if self._blink_id is not None:
            try:
                GLib.source_remove(self._blink_id)
            except Exception:
                pass
            self._blink_id = None
        self.icon_label.set_label(self.stop_icon)
        return False

    def _leave_button(self, *event):
        self.blink = True
        self.icon_label.set_label(self.first_icon)
        if self.blink and self.icons_enable and self._blink_id is None:
            try:
                self._blink_id = GLib.timeout_add(self.blink_interval, self._blink_tick)
            except Exception:
                self._blink_id = None
        GLib.idle_add(self._start_timer)
        return False

    def _press_button(self, *event):
        self._stop_timer()
        self.recorder_service.stop_recording()
        self.icon_button.hide()
        self.hide()
        self.json.update(STATUS_BAR_LOCK_MODULES, "screen_recorder.is_recording", False)
        self.json.update(STATUS_BAR_LOCK_MODULES, "screen_recorder.seconds", 0)
        return False

    @staticmethod
    def _to_bool(value) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return bool(value)
        s = str(value).strip().lower()
        return s in ("1", "true", "on", "start", "started", "yes")

    def _format_time(self, seconds: int) -> str:
        if seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            if self.is_horizontal:
                return f"{minutes:02}:{secs:02}"
            return f"{minutes:02}\n{secs:02}"

        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if self.is_horizontal:
                return f"{hours:02}:{minutes:02}:{secs:02}"
            return f"{hours:02}\n{minutes:02}\n{secs:02}"

    def _blink_tick(self) -> bool:
        if not (self.icons_enable and self.blink):
            self._blink_id = None
            return False

        self._icon_state = not self._icon_state

        try:
            self.icon_label.set_label(
                self.second_icon if self._icon_state else self.first_icon
            )
            if self._icon_state:
                self.icon_label.get_style_context().add_class("mig")
            else:
                self.icon_label.get_style_context().remove_class("mig")
        except Exception:
            pass
        return True

    def _timer_tick(self) -> bool:
        self._seconds += 1
        try:
            self.timer_label.set_label(self._format_time(self._seconds))
            self.json.update(
                STATUS_BAR_LOCK_MODULES, "screen_recorder.seconds", self._seconds
            )
        except Exception:
            pass
        return True

    def _add_container_style(self):
        try:
            self.get_style_context().add_class("statusbar-screen-recorder")
        except Exception:
            pass

    def _remove_container_style(self):
        try:
            self.get_style_context().remove_class("statusbar-screen-recorder")
        except Exception:
            pass

    def _start_timer(self):
        if self._timer_id is not None or (self.blink and self._blink_id is not None):
            try:
                self.show()
                if self.icons_enable:
                    self.child_box.show()
                if self.timer:
                    self.timer_label.show()
            except Exception:
                pass
            return

        self._add_container_style()

        try:
            self.show()
            if self.icons_enable:
                self.child_box.show()
            if self.timer:
                self.timer_label.show()
        except Exception:
            pass

        self._seconds = self.default_seconds
        self._icon_state = True
        if self.timer:
            self.timer_label.set_label(self._format_time(self._seconds))
        if self.icons_enable:
            self.icon_label.set_label(self.first_icon)

        if self.timer and self._timer_id is None:
            self._timer_id = GLib.timeout_add_seconds(1, self._timer_tick)
        if self.blink and self.icons_enable and self._blink_id is None:
            self._blink_id = GLib.timeout_add(self.blink_interval, self._blink_tick)

    def _stop_timer(self):
        if self._timer_id is not None:
            try:
                GLib.source_remove(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

        if self._blink_id is not None:
            try:
                GLib.source_remove(self._blink_id)
            except Exception:
                pass
            self._blink_id = None

        self._seconds = self.default_seconds
        try:
            self.timer_label.set_label("")
            self.icon_label.set_label(self.first_icon)
        except Exception:
            pass

        try:
            self.child_box.hide()
            self.timer_label.hide()
            self.hide()
            self._remove_container_style()
        except Exception:
            pass

    def on_recording_change(self, *args):
        try:
            raw_val = args[-1] if args else False
            is_recording = self._to_bool(raw_val)

            logger.debug("[ScreenRecording] on_recording_change -> {}", is_recording)

            if is_recording:
                self.show_all()
                self.icon_button.show()
                self._stop_timer()

                self.json.update(
                    STATUS_BAR_LOCK_MODULES, "screen_recorder.is_recording", True
                )

                self.default_seconds = self.json.get_with_dot_data(
                    STATUS_BAR_LOCK_MODULES, "screen_recorder.seconds"
                )
                self._seconds = self.default_seconds
                self.timer_label.set_label(self._format_time(self._seconds))

                GLib.idle_add(self._start_timer)

            else:
                self.json.update(
                    STATUS_BAR_LOCK_MODULES, "screen_recorder.is_recording", False
                )
                self.json.update(STATUS_BAR_LOCK_MODULES, "screen_recorder.seconds", 0)

                self.default_seconds = 0
                self._seconds = 0
                self.timer_label.set_label("")

                GLib.idle_add(self._stop_timer)

        except Exception as e:
            logger.exception(
                "[ScreenRecording] exception in on_recording_change: {}", e
            )
            pass
