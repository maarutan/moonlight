from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label

from utils.widget_utils import setup_cursor_hover
from .tray_items import TrayItems
from typing import Callable

from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.grid import Grid
from fabric.widgets.scrolledwindow import ScrolledWindow

from gi.repository import Gtk, Gdk, GLib  # type:ignore


class TrayBox(Window):
    def __init__(
        self,
        position: str,
        bar_position: str,
        do_click_handler: Callable,
        is_horizontal: bool = True,
        spacing: int = 8,
        pixel_size: int = 20,
        refresh_interval: int = 1,
    ):
        self.spacing = spacing
        self.refresh_interval = refresh_interval
        self.pixel_size = pixel_size

        self.is_horizontal = is_horizontal
        self.position = position
        self.bar_position = bar_position
        self.do_click_handler = do_click_handler
        super().__init__(
            name="statusbar-tray-box-container",
            layer="overlay",
            anchor=position,
            exclusivity="auto",
            all_visible=True,
            h_align="fill",
            v_align="fill",
            child=self._make_content(),
            margin=self.margin_handler(),
            focusable=True,
        )

        self.set_can_focus(True)
        self.user_closed = False

        self.connect("focus-out-event", self._on_focus_out)
        self.connect("leave-notify-event", self._on_mouse_leave)
        self.add_events(
            Gdk.EventMask.FOCUS_CHANGE_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self._ignore_close_click = False

    def _make_content(self):
        wrapper_on_main_box = EventBox(name="statusbar-tray-box-wrapper", spacing=0)
        main_box = Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content = Grid(name="statusbar-tray-box", all_visible=True)
        tray = TrayItems(
            is_horizontal=self.is_horizontal,
            pixel_size=self.pixel_size,
            refresh_interval=self.refresh_interval,
            grid=True,
            spacing=self.spacing,
        )
        content.attach(tray, 0, 1, 1, 1)
        content.set_row_spacing(10)

        scrolled = ScrolledWindow(name="statusbar-tray-box-scrolled")
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        scrolled.set_overlay_scrolling(False)
        scrolled.add(content)
        scrolled.set_min_content_height(160)
        content.set_size_request(190, 190)

        close_button = Button(
            name="statusbar-tray-box-close",
            label="",
            on_clicked=self._on_close_clicked,
        )
        setup_cursor_hover(close_button, "pointer")
        main_box.add(
            EventBox(
                child=CenterBox(
                    name="statusbar-tray-box-title-container",
                    start_children=Label(
                        name="statusbar-tray-box-title", label="System Tray"
                    ),
                    end_children=close_button,
                )
            )
        )
        main_box.pack_start(scrolled, True, True, 0)
        wrapper_on_main_box.add(main_box)
        return wrapper_on_main_box

    def _on_close_clicked(self, *args):
        self.user_closed = True
        if self.do_click_handler:
            self.do_click_handler()
        self.hide()

    def _on_focus_out(self, widget, event):
        if not self._ignore_close_click:
            self._ignore_close_click = True
            self._on_close_clicked()
            GLib.timeout_add(100, self._reset_ignore_flag)

    def _reset_ignore_flag(self):
        self._ignore_close_click = False
        return False

    def _on_mouse_leave(self, widget, event):
        if not self._ignore_close_click:
            self._ignore_close_click = True
            self._on_close_clicked()
            GLib.timeout_add(100, self._reset_ignore_flag)

    def margin_handler(self) -> str:
        pos = self.position
        barpos = self.bar_position

        if barpos == "top":
            if pos == "top right":
                return "30 220 0 0"
            elif pos == "top":
                return "30 0 0 0"
            elif pos == "top left":
                return "30 0 0 220"
        elif barpos == "left":
            if pos == "top left":
                return "120 30 0 0"
            elif pos == "center left":
                return "0 0 0 30"
            elif pos == "bottom left":
                return "0 0 120 30"
        elif barpos == "right":
            if pos == "top right":
                return "120 30 0 0"
            elif pos == "center right":
                return "0 0 0 30"
            elif pos == "bottom right":
                return "0 30 120  0"
        elif barpos == "bottom":
            if pos == "bottom left":
                return "0 0 30 120"
            elif pos == "bottom":
                return "0 0 30 0"
            elif pos == "bottom right":
                return "0 120 30  0"

        return "0 0 0 0"
