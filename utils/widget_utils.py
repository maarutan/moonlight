from typing import Any, Literal, Optional
from gi.repository import Gdk  # type:ignore
from fabric.utils import bulk_connect


def setup_cursor_hover(
    widget,
    cursor_name: Literal["pointer", "crosshair", "grab"] = "pointer",
) -> None:
    display = Gdk.Display.get_default()
    cursor = Gdk.Cursor.new_from_name(display, cursor_name)  # type:ignore

    if cursor is None:
        return

    def _set_cursor(w, cur):
        win = w.get_window()
        if win is not None:
            win.set_cursor(cur)

    def on_enter_notify_event(w, _event):
        _set_cursor(w, cursor)
        return False

    def on_leave_notify_event(w, _event):
        _set_cursor(w, None)
        return False

    bulk_connect(
        widget,
        {
            "enter-notify-event": on_enter_notify_event,
            "leave-notify-event": on_leave_notify_event,
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
