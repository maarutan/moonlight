from fabric.utils.helpers import Gtk
from fabric.hyprland.service import Hyprland
from typing import Callable


hypr = Hyprland()


def event_close_popup(
    callback: Callable,
    ignore_event: str = "",
):
    events = [
        "activewindow",
        "moveworkspace",
        "fullscreen",
        "changeFloatingMode",
        "openWindow",
        "closeWindow",
    ]
    for e in events:
        if e == ignore_event:
            continue
        hypr.connect(f"event::{e}", callback)


def click_widget(widget: Gtk.Widget, callback: Callable):
    widget.connect("button-press-event", callback)
