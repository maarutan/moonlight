from .corners import MyCorner, ScreenCorners
from .status_bar.bar import StatusBar
from .activate_linux import ActivateLinux
from .notification import NotificationPopup
from .dock_station.dock import Dock
from .player.player import PlayerWrapper
from .desktop_clock import DesktopClock
from .language_preview.language_preview import LanguagePreview
from .battery_alert.alert import BatteryAlert
from ._core_.modules_handler import ModulesHandler
from .screen_menu import ScreenMenu

__all__ = [
    "MyCorner",
    "DesktopClock",
    "ScreenCorners",
    "ActivateLinux",
    "ScreenMenu",
    "PlayerWrapper",
    "StatusBar",
    "NotificationPopup",
    "LanguagePreview",
    "Dock",
    "BatteryAlert",
    "ModulesHandler",
]
