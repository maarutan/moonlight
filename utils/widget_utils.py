import socket
import subprocess
from typing import (
    Any,
    Literal,
    Optional,
    Callable,
    Tuple,
)
from fabric.utils import Gtk, bulk_connect, Gdk
from fabric.utils.helpers import Gtk
from fabric.hyprland.service import Hyprland
from typing import Callable


hypr = Hyprland()


def set_cursor_now(widget, cursor_name: str | None):
    display = Gdk.Display.get_default()
    cursor = None

    if cursor_name is not None:
        try:
            cursor = Gdk.Cursor.new_from_name(display, cursor_name)
        except Exception:
            cursor = None

    top = widget.get_toplevel()
    win = top.get_window() if top else widget.get_window()
    if win:
        win.set_cursor(cursor)


def setup_cursor_hover(
    widget,
    cursor_name: Literal["pointer", "crosshair", "grab"] = "pointer",
    press_cursor_name: Literal["pointer", "crosshair", "grab"] = "grab",
) -> None:
    display = Gdk.Display.get_default()
    default_cursor = None
    press_cursor = None

    try:
        default_cursor = Gdk.Cursor.new_from_name(display, cursor_name)  # type: ignore
    except Exception:
        default_cursor = None

    try:
        press_cursor = Gdk.Cursor.new_from_name(display, press_cursor_name)  # type: ignore
    except Exception:
        press_cursor = None

    def _set_cursor_on_window(win, cur):
        if win is not None:
            win.set_cursor(cur)

    def _set_cursor_on_toplevel(w, cur):
        top = w.get_toplevel()
        win = top.get_window() if top is not None else w.get_window()
        _set_cursor_on_window(win, cur)

    def on_enter_notify_event(w, _event):
        _set_cursor_on_toplevel(w, default_cursor)
        return False

    def on_leave_notify_event(w, _event):
        _set_cursor_on_toplevel(w, None)
        return False

    def on_button_press_event(w, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            _set_cursor_on_toplevel(w, press_cursor)
        return False

    def on_button_release_event(w, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 1:
            _set_cursor_on_toplevel(w, default_cursor)
        return False

    widget.add_events(
        Gdk.EventMask.ENTER_NOTIFY_MASK  # type: ignore
        | Gdk.EventMask.LEAVE_NOTIFY_MASK  # type: ignore
        | Gdk.EventMask.BUTTON_PRESS_MASK  # type: ignore
        | Gdk.EventMask.BUTTON_RELEASE_MASK  # type: ignore
    )

    bulk_connect(
        widget,
        {
            "enter-notify-event": on_enter_notify_event,
            "leave-notify-event": on_leave_notify_event,
            "button-press-event": on_button_press_event,
            "button-release-event": on_button_release_event,
        },
    )


def merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result


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


def bar_margin_handler(
    position: str,
    layout_config: str,
    default_value: Any,
    widget_name: str,
    px: int = 30,
) -> str:
    section: Optional[str] = None
    for sec_name, widgets in layout_config.items():  # type: ignore
        for w in widgets:
            if isinstance(w, str) and widget_name in w:
                section = sec_name
                break

    px = 30
    m = f"{px}px"

    margin = {
        "start": {
            "top": f"{m} 0 {m} {m}",
            "bottom": f"{m} 0 {m} {m}",
            "left": f"{m} {m} 0 {m}",
            "right": f"{m} {m} 0 {m}",
        },
        "center": {
            "top": f"0 0 {m} 0",
            "bottom": f"{m} 0 0 0",
            "left": f"{m} {m} {m} {m}",
            "right": f"{m} {m} {m} {m}",
        },
        "end": {
            "top": f"0 {m} {m} 0",
            "bottom": f"{m} {m} 0 0",
            "left": f"{m} 0 {m} {m}",
            "right": f"{m} {m} {m} 0",
        },
    }

    return margin.get(section, {}).get(  # type: ignore
        position,
        default_value,
    )


def bar_anchor_handler(
    widget_name: str,
    position: str,
    layout_config: dict,
    default_value: Any,
) -> str:
    section: Optional[str] = None
    for sec_name, widgets in layout_config.items():
        if any(isinstance(w, str) and widget_name in w for w in widgets):
            section = sec_name
            break

    anchors = {
        "start": {
            "top": "top left",
            "bottom": "bottom left",
            "left": "top left",
            "right": "top right",
        },
        "center": {
            "top": "top center",
            "bottom": "bottom center",
            "left": "center left",
            "right": "center right",
        },
        "end": {
            "top": "top right",
            "bottom": "bottom right",
            "left": "bottom left",
            "right": "bottom right",
        },
    }

    return anchors.get(section, {}).get(  # type: ignore
        position,
        default_value,
    )


def check_internet(timeout: float = 0.5) -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False
