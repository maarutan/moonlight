from typing import Literal
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
