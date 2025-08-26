# services/screen_record.py
import traceback
from dataclasses import dataclass
from loguru import logger
from fabric.core.service import Service, Signal
from fabric.utils.helpers import idle_add
from gi.repository import GLib  # type: ignore
from typing import Callable


@dataclass(frozen=True)
class HyprlandEvent:
    name: str
    data: list[str]
    raw_data: bytes


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
        self._confirm_timer_id = None
        self._pending_state = None

        self._bg_check_id = None

        self._probe_funcs: list[Callable[[], object]] | None = None

        if not self._init_hypr():
            self._retry_timer_id = GLib.timeout_add_seconds(2, self._try_init_hypr)

        self._bg_check_id = GLib.timeout_add(2000, self._background_check)

        idle_add(self._immediate_probe_and_set)

    def start_recording(self) -> None:
        """Явно пометить запись активной и эмитнуть сигнал."""
        self._apply_state(True)

    def stop_recording(self) -> None:
        """Явно пометить запись остановленной и эмитнуть сигнал."""
        self._apply_state(False)

    def _try_init_hypr(self) -> bool:
        ok = self._init_hypr()

        return not ok

    def _init_hypr(self) -> bool:
        try:
            from fabric.hyprland.service import Hyprland

            self._hypr = Hyprland()

            try:
                self._hypr.connect("event::screencast", self._on_screencast_event)
            except Exception:
                logger.debug(
                    "[ScreenRecorderService] failed to connect screencast event"
                )
            logger.info("[ScreenRecorderService] connected to Hyprland events socket")

            if self._retry_timer_id:
                try:
                    GLib.source_remove(self._retry_timer_id)
                except Exception:
                    pass
                self._retry_timer_id = None

            candidates = [
                "is_screencast_active",
                "screencast_active",
                "get_screencast_state",
                "get_screencast",
                "is_recording",
                "screencast_state",
                "have_screencast",
                "screencast",
                "screencast_is_active",
            ]
            funcs: list[Callable[[], object]] = []
            for name in candidates:
                try:
                    attr = getattr(self._hypr, name, None)
                    if attr is None:
                        continue
                    if callable(attr):
                        funcs.append(attr)
                    else:
                        funcs.append(lambda v=attr: v)
                except Exception:
                    continue
            self._probe_funcs = funcs

            idle_add(self._immediate_probe_and_set)
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

            logger.debug(
                "[ScreenRecorderService] parsed screencast state -> %s", new_state
            )

            if new_state == self.is_recording:
                logger.debug(
                    "[ScreenRecorderService] screencast state unchanged -> %s",
                    new_state,
                )
                return

            self._schedule_confirm(new_state)
        except Exception as e:
            logger.error(
                "[ScreenRecorderService] exception in _on_screencast_event: {}", e
            )
            logger.debug(traceback.format_exc())

    def _schedule_confirm(self, new_state: bool):
        self._pending_state = new_state
        if self._confirm_timer_id is not None:
            try:
                GLib.source_remove(self._confirm_timer_id)
            except Exception:
                pass
            self._confirm_timer_id = None

        probe = self._probe_state()
        if probe is not None and probe == new_state:
            self._apply_state(new_state)
            self._pending_state = None
            return

        self._confirm_timer_id = GLib.timeout_add(250, self._confirm_pending_state)

    def _confirm_pending_state(self) -> bool:
        try:
            pending = self._pending_state

            self._confirm_timer_id = None
            if pending is None:
                return False

            probe = self._probe_state()

            if probe is not None and probe != pending:
                self._pending_state = None
                return False

            self._apply_state(pending)
        except Exception as e:
            logger.error(
                "[ScreenRecorderService] exception in _confirm_pending_state: {}", e
            )
            logger.debug(traceback.format_exc())
        finally:
            self._pending_state = None

        return False

    def _apply_state(self, state: bool):
        if state == self.is_recording:
            return

        self.is_recording = state

        try:
            idle_add(lambda: self.recording.emit(state))
        except Exception:
            try:
                self.recording.emit(state)
            except Exception:
                logger.debug("[ScreenRecorderService] failed to emit recording signal")
        logger.info(
            "[ScreenRecorderService] screencast -> {}", "active" if state else "stopped"
        )

    def _probe_state(self):
        try:
            if self._hypr is None:
                if not self._init_hypr():
                    return None

            if not self._probe_funcs:
                return None

            for func in self._probe_funcs:
                try:
                    val = func()
                except Exception:
                    continue

                if isinstance(val, bool):
                    return val
                if isinstance(val, (int, float)):
                    return bool(val)
                if isinstance(val, str):
                    s = val.strip().lower()
                    if s in ("1", "true", "start", "started", "on"):
                        return True
                    if s in ("0", "false", "stop", "stopped", "off"):
                        return False
            return None
        except Exception as e:
            logger.debug("[ScreenRecorderService] exception in _probe_state: {}", e)
            logger.debug(traceback.format_exc())
            return None

    def _background_check(self) -> bool:
        try:
            probe = self._probe_state()
            if probe is None:
                return True
            if probe != self.is_recording:
                self._apply_state(probe)
                logger.info(
                    "[ScreenRecorderService] background check -> {}",
                    "active" if probe else "stopped",
                )
        except Exception as e:
            logger.error(
                "[ScreenRecorderService] exception in _background_check: {}", e
            )
            logger.debug(traceback.format_exc())

        return True

    def _immediate_probe_and_set(self):
        try:
            probe = self._probe_state()
            if probe is None:
                return False
            if probe != self.is_recording:
                self._apply_state(probe)
        except Exception:
            logger.debug(
                "[ScreenRecorderService] exception in _immediate_probe_and_set"
            )
            logger.debug(traceback.format_exc())

        return False
