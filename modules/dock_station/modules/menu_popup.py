from fabric.widgets.wayland import WaylandWindow as Window
from utils.json_manager import JsonManager


class PopupMenu(Window):
    def __init__(self, anchor: str):
        super().__init__(
            name="dock-station-popup-menu",
            anchor=anchor,
            layer="top",
        )
