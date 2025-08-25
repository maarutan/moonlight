from loguru import logger

from ...modules.screen_recording import ScreenRecording

from .cavalcade import cavalcade_handler
from .profile import profile_handler
from .clock import clock_handler
from .language import language_handler
from .workspaces import workspaces_handler
from .memory_ram import memory_ram_handler
from .system_tray import system_tray_handler
from .windows_title import windows_title_handler
from .metrics import metrics_handler
# from .media_player_windows_title import mp_windows_title_handler

MODULES_REGISTRY = {
    "clock": clock_handler,
    "profile": profile_handler,
    "language": language_handler,
    "workspaces": workspaces_handler,
    "windows-title": windows_title_handler,
    # "media-player-with-windows-title": mp_windows_title_handler,
    "system-tray": system_tray_handler,
    "memory": memory_ram_handler,
    "metrics": metrics_handler,
    "cavalcade": cavalcade_handler,
    "screen-recording": lambda _: ScreenRecording(),
}


def init_modules(conf) -> dict[str, object]:
    built_modules = {}
    for key, handler in MODULES_REGISTRY.items():
        try:
            built_modules[key] = handler(conf)
        except Exception as e:
            logger.error(f"[Module Error] Failed to initialize '{key}': {e}")
    return built_modules
