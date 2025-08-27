from ...modules.screen_recorder import ScreenRecorder
from .._config_handler import ConfigHandler


def screen_recorder_handler(cfg: ConfigHandler) -> ScreenRecorder:
    return ScreenRecorder(
        icons_enable=cfg.screen_recorder.icons()["enable"],
        first_icon=cfg.screen_recorder.icons()["first"],
        second_icon=cfg.screen_recorder.icons()["second"],
        stop_icon=cfg.screen_recorder.icons()["stop"],
        blink=cfg.screen_recorder.blink()["enable"],
        is_horizontal=cfg.bar.is_horizontal(),
        blink_interval=cfg.screen_recorder.blink()["interval"],
        timer=cfg.screen_recorder.timer(),
    )
