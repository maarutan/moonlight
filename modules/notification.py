from fabric.notifications import (
    Notification,
    NotificationAction,
    NotificationCloseReason,
)
from fabric.utils import bulk_connect, get_relative_path
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.eventbox import EventBox
from fabric.widgets.grid import Grid
from fabric.widgets.label import Label
from fabric.widgets.revealer import Revealer
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import Gdk, GdkPixbuf, GLib  # type: ignore


class NotificationWidget(Box):
    def __init__(
        self,
        orientation_pos: bool = True,
        timeout_s: int = 4,
    ):
        self.timeout_s = timeout_s * 1000
        super().__init__(
            name="notification-box",
            orientation=orientation_pos,
            h_expand=True,
            v_expand=True,
            h_align="fill",
            v_align="fill",
        )


class NotificationPopup(Window):
    def __init__(self):
        super().__init__(
            name="notification",
            all_visible=True,
            layer="top left",
            h_align="fill",
            v_align="fill",
        )
