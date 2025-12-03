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
