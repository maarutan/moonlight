# services/screen_record.py
import traceback
from dataclasses import dataclass
from loguru import logger
from fabric.core.service import Service, Signal
from fabric.utils.helpers import idle_add
from gi.repository import GLib  # type: ignore


@dataclass(frozen=True)
class HyprlandEvent:
    name: str
    data: list[str]
    raw_data: bytes


# Singleton holder
_instance: "ScreenRecorderService | None" = None


def get_screen_recorder() -> "ScreenRecorderService":
    global _instance
    if _instance is None:
        _instance = ScreenRecorderService()
    return _instance


class ScreenRecorderService(Service):
    @Signal
    def recording(self, value: bool): ...

    def __init__(self):
        super().__init__()
        self._hypr = None
        self.is_recording = False
        self._retry_timer_id = None

        if not self._init_hypr():
            self._retry_timer_id = GLib.timeout_add_seconds(2, self._try_init_hypr)

    def _try_init_hypr(self) -> bool:
        ok = self._init_hypr()
        return not ok

    def _init_hypr(self) -> bool:
        try:
            from fabric.hyprland.service import Hyprland  # type: ignore

            self._hypr = Hyprland()
            self._hypr.connect("event::screencast", self._on_screencast_event)
            logger.info("[ScreenRecorderService] connected to Hyprland events socket")
            if self._retry_timer_id:
                try:
                    GLib.source_remove(self._retry_timer_id)
                except Exception:
                    pass
                self._retry_timer_id = None
            return True
        except Exception as e:
            logger.warning(
                "[ScreenRecorderService] can't init Hyprland service yet: {}", e
            )
            logger.debug(traceback.format_exc())
            return False

    def _on_screencast_event(self, service, event: HyprlandEvent):
        try:
            logger.debug(
                "[ScreenRecorderService] screencast raw=%r data=%r",
                getattr(event, "raw_data", None),
                getattr(event, "data", None),
            )

            state_token = None
            if getattr(event, "data", None):
                if len(event.data) > 0:
                    state_token = str(event.data[0])
            else:
                raw = getattr(event, "raw_data", b"")
                try:
                    raw_s = raw.decode(errors="ignore")
                    if ">>" in raw_s:
                        body = raw_s.split(">>", 1)[1]
                        state_token = body.split(",")[0].strip()
                except Exception:
                    state_token = None

            if state_token is None:
                logger.warning(
                    "[ScreenRecorderService] unknown screencast payload, ignoring (raw=%r)",
                    getattr(event, "raw_data", None),
                )
                return

            s = state_token.lower().strip()
            new_state = s in ("1", "true", "start", "started", "on")
            if s in ("0", "false", "stop", "stopped", "off"):
                new_state = False

            if new_state != self.is_recording:
                self.is_recording = new_state
                idle_add(lambda: self.recording.emit(new_state))
                logger.info(
                    "[ScreenRecorderService] screencast -> {}",
                    "active" if new_state else "stopped",
                )
            else:
                logger.debug(
                    "[ScreenRecorderService] screencast state unchanged -> {}",
                    new_state,
                )
        except Exception as e:
            logger.error(
                "[ScreenRecorderService] exception in _on_screencast_event: {}", e
            )
            logger.debug(traceback.format_exc())
