from ..menu.app_menu import build_app_menu

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...dock import DockStation


class AppContextMenu:
    def __init__(self, dockstation: "DockStation", app_name):
        self.dockstation = dockstation
        self.menu = build_app_menu(dockstation, app_name)

        self.menu.connect("deactivate", self.on_show)
        self.menu.connect("selection-done", self.on_show)

    def on_show(self):
        self.dockstation.tools.toggle("show")

    def popup(self, widget):
        self.menu.popup(widget)
