from loguru import logger
from gi.repository import GLib  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from services.screen_record import get_screen_recorder


class ScreenRecorder(Box):
    def __init__(
        self,
        icons_enable: bool = True,
        first_icon: str = "󰄘",
        second_icon: str = "󰄙",
        blink: bool = True,
        blink_interval: int = 400,
        timer: bool = True,
    ):
        self.first_icon = first_icon
        self.second_icon = second_icon
        self.blink = blink
        self.timer = timer

        super().__init__(
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
            orientation="h",
        )

        self.default_seconds = 0
        self.icons_enable = icons_enable
        self.icon_label = Label(
            name="rec-icon", label=self.first_icon if self.icons_enable else ""
        )
        self.timer_label = Label(name="screen-recording-icon", label="")
        self.blink_interval = blink_interval
        self._icon_state = True

        self.child_box = Box(name="indicator")
        self.child_box.add(self.icon_label)
        if self.icons_enable:
            self.child_box.remove_style_class("indicator")

        self.add(self.child_box)
        self.add(self.timer_label)

        try:
            self.set_no_show_all(True)
            self.child_box.set_no_show_all(True)
            self.timer_label.set_no_show_all(True)
        except Exception:
            pass

        self.child_box.hide()
        self.timer_label.hide()
        self.hide()

        self.recorder_service = get_screen_recorder()
        self.recorder_service.recording.connect(self.on_recording_change)

        GLib.idle_add(self._stop_timer)

        self._seconds = self.default_seconds
        self._timer_id = None
        self._blink_id = None

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
            return f"{minutes:02}:{secs:02}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours:02}:{minutes:02}:{secs:02}"

    def _blink_tick(self) -> bool:
        if not (self.icons_enable and self.blink):
            return False

        if not self.icons_enable:
            return True

        self._icon_state = not self._icon_state
        self.icon_label.set_label(
            self.second_icon if self._icon_state else self.first_icon
        )
        try:
            if self._icon_state:
                self.icon_label.get_style_context().add_class("mig")
            else:
                self.icon_label.get_style_context().remove_class("mig")
        except Exception:
            pass
        return True

    def _timer_tick(self) -> bool:
        self._seconds += 1
        self.timer_label.set_label(self._format_time(self._seconds))
        return True

    def _add_container_style(self):
        try:
            if self.timer:
                self.add_style_class("statusbar-screen-recording")
        except Exception:
            try:
                self.get_style_context().add_class("statusbar-screen-recording")
            except Exception:
                pass

    def _remove_container_style(self):
        try:
            self.get_style_context().remove_class("statusbar-screen-recording")
        except Exception:
            pass

    def _start_timer(self):
        self._add_container_style()

        self.show()
        if self.icons_enable:
            self.child_box.show()
        if self.timer:
            self.timer_label.show()

        self._seconds = self.default_seconds
        self._icon_state = True
        if self.timer:
            self.timer_label.set_label("00:00")
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
        self.timer_label.set_label("")
        self.icon_label.set_label(self.first_icon)

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
            logger.debug(
                "[ScreenRecording] on_recording_change args=%r -> parsed=%s",
                args,
                is_recording,
            )
            if is_recording:
                GLib.idle_add(self._start_timer)
            else:
                GLib.idle_add(self._stop_timer)
        except Exception as e:
            logger.exception(
                "[ScreenRecording] exception in on_recording_change: {}", e
            )
