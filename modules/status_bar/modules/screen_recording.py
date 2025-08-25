from loguru import logger
from gi.repository import GLib
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from services.screen_record import get_screen_recorder


class ScreenRecording(Box):
    def __init__(self):
        self.hide()
        super().__init__(
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
            orientation="h",
        )

        self.timer_label = Label(name="screen-recording-icon", label="")
        self.icon_label = Label(name="rec-icon", label="󰑋")
        self._icon_state = True

        self.children = [
            Box(name="indicator", children=[self.icon_label]),
            self.timer_label,
        ]

        self.add_style_class("statusbar-screen-recording")

        self.recorder_service = get_screen_recorder()
        self.recorder_service.recording.connect(self.on_recording_change)

        self._seconds = 0
        self._timer_id = None

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
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    def _update_timer(self):
        self._seconds += 1
        self.timer_label.set_label(self._format_time(self._seconds))
        self._icon_state = not self._icon_state
        self.icon_label.set_label("󰑊" if self._icon_state else "󰑋")

        if self._icon_state:
            self.icon_label.get_style_context().add_class("mig")
        else:
            self.icon_label.get_style_context().remove_class("mig")
        return True

    def _start_timer(self):
        self._seconds = 0
        self._icon_state = True
        self.show()
        self.timer_label.set_label("00:00")
        self.icon_label.set_label("󰑋")
        if self._timer_id is None:
            self._timer_id = GLib.timeout_add_seconds(1, self._update_timer)

    def _stop_timer(self):
        if self._timer_id is not None:
            try:
                GLib.source_remove(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        self._seconds = 0
        self.timer_label.set_label("")
        self.icon_label.set_label("󰑋")
        self.hide()

    def on_recording_change(self, *args):
        self.show_all()
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
