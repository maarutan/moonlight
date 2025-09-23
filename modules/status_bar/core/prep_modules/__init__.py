from loguru import logger

from .._config_handler import ConfigHandlerStatusBar


from .cavalcade import cavalcade_handler
from .profile import profile_handler
from .clock import clock_handler
from .language import language_handler
from .workspaces import workspaces_handler
from .memory_ram import memory_ram_handler
from .system_tray import system_tray_handler
from .windows_title import windows_title_handler
from .metrics import metrics_handler
from .screen_recorder import screen_recorder_handler
from .battery import battery_handler
from .check_update import check_update_handler
from .network_speed import network_speed_handler


MODULES_REGISTRY = {
    "clock": clock_handler,
    "profile": profile_handler,
    "language": language_handler,
    "workspaces": workspaces_handler,
    "windows-title": windows_title_handler,
    # "media-player-with-windows-title": mp_windows_title_handler,
    "system-tray": system_tray_handler,
    "network-speed": network_speed_handler,
    "memory": memory_ram_handler,
    "metrics": metrics_handler,
    "cavalcade": cavalcade_handler,
    "screen-recorder": screen_recorder_handler,
    "battery": battery_handler,
    "check-update": check_update_handler,
}


def init_modules(cfg: ConfigHandlerStatusBar) -> dict[str, object]:
    built_modules = {}
    seen = set()

    def _get_list(key: str) -> list[str]:
        value = cfg._get_options(key, [])
        if not isinstance(value, list):
            return []
        return value

    all_modules = (
        _get_list("modules-start")
        + _get_list("modules-center")
        + _get_list("modules-end")
    )

    for key in all_modules:
        if key in seen:
            continue
        seen.add(key)
        handler = MODULES_REGISTRY.get(key)
        if not handler:
            logger.warning(f"[Module Warning] '{key}' not found in registry")
            continue
        try:
            built_modules[key] = handler(cfg)
        except Exception as e:
            logger.error(f"[Module Error] Failed to initialize '{key}': {e}")

    return built_modules
