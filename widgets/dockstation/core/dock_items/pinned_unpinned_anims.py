# pinned_unpinned_anims.py
from typing import TYPE_CHECKING, Callable, Optional
from fabric.utils import Gtk, GLib
from fabric.widgets.label import Label
from shared.app_icon import AppIcon

if TYPE_CHECKING:
    from .items import DockStationItems


class PinAnimator:
    def __init__(self, items: "DockStationItems"):
        self.items = items
        self.dock = items.dockstation
