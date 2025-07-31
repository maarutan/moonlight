from .system_tray_base import TrayItems
from typing import Callable

from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.grid import Grid

from gi.repository import Gtk, Gdk, GLib  # type:ignore


class TrayBox(Window):
    def __init__(self, position: str, bar_position: str, do_click_handler: Callable):
        self.position = position
        self.bar_position = bar_position
        self.do_click_handler = do_click_handler
        super().__init__(
            name="tray-box-container",
            layer="top",
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
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content = Grid(name="tray-box", all_visible=True)
        tray = TrayItems()
        content.attach(tray, 0, 1, 1, 1)
        content.set_row_spacing(10)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        scrolled.set_overlay_scrolling(False)
        scrolled.add(content)
        scrolled.set_min_content_height(100)
        content.set_size_request(190, 190)

        main_box.pack_start(scrolled, True, True, 0)

        close_button = Gtk.Button(label="Close 🚪")
        close_button.connect("clicked", self._on_close_clicked)
        self.close_button = close_button
        main_box.pack_start(close_button, False, False, 0)

        return main_box

    def _on_close_clicked(self, button=None, *args):
        self.user_closed = True
        if self.do_click_handler:
            self.do_click_handler()
        self.hide()

    def _on_focus_out(self, widget, event):
        if not self._ignore_close_click:
            self._ignore_close_click = True
            self.close_button.emit("clicked")
            GLib.timeout_add(100, self._reset_ignore_flag)

    def _reset_ignore_flag(self):
        self._ignore_close_click = False
        return False

    def _on_mouse_leave(self, widget, event):
        if not self._ignore_close_click:
            self._ignore_close_click = True
            self.close_button.emit("clicked")
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
