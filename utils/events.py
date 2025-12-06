from fabric.utils.helpers import Gtk
from fabric.hyprland.service import Hyprland
from typing import Callable


hypr = Hyprland()


def event_close_popup(callback: Callable):
    events = [
        "activewindow",
        "moveworkspace",
        "fullscreen",
        "changeFloatingMode",
        "openWindow",
        "closeWindow",
    ]
    for e in events:
        hypr.connect(f"event::{e}", callback)


def click_widget(widget: Gtk.Widget, callback: Callable):
    widget.connect("button-press-event", callback)
