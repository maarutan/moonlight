from typing import TYPE_CHECKING
from modules.screen_menu.menu import ScreenMenu

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


def screen_menu_handler(cfg: "CoreConfigHandler") -> ScreenMenu:
    return ScreenMenu(
        enabled=cfg.screen_menu.enabled(),
        list_items=cfg.screen_menu.list_items(),
    )
