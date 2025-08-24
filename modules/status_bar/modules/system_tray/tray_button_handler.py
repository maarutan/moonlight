from .tray_box import TrayBox
import json

from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.hyprland.service import Hyprland, HyprlandEvent

from gi.repository import Gdk  # type: ignore


class TrayButtonHandler(Box):
    def __init__(
        self,
        tray_box_position: str,
        bar_position: str,
        is_horizontal: bool = True,
        spacing: int = 8,
        pixel_size: int = 20,
        refresh_interval: int = 1,
    ):
        self.spacing = spacing
        self.pixel_size = pixel_size
        self.refresh_interval = refresh_interval
        super().__init__(
            name="tray-handler-container", orientation="h" if is_horizontal else "v"
        )
        self.connection = Hyprland()
        self.last_window_address = None
        self.connection.connect("event::activewindow", self._on_active_window)

        if self.connection.ready:
            self._initialize_last_window()
        else:
            self.connection.connect(
                "event::ready", lambda _: self._initialize_last_window()
            )

        self.button = Button(
            name="statusbar-tray-button",
            h_align="fill",
            v_align="fill",
            all_visible=True,
            h_expand=True,
            v_expand=True,
            on_clicked=self.do_clicked,
            label="",
        )

        inner = Box(name="tray-handler-inner", all_visible=True)
        inner.add(self.button)
        self.add(inner)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self._on_box_click)

        self.tray = TrayBox(
            position=tray_box_position,
            bar_position=bar_position,
            do_click_handler=self.do_clicked,
            spacing=self.spacing,
            pixel_size=self.pixel_size,
            refresh_interval=self.refresh_interval,
        )
        self.tray.hide()

    def _initialize_last_window(self):
        win_data = self.connection.send_command("j/activewindow").reply.decode()
        win_json = json.loads(win_data)
        self.last_window_address = win_json.get("address")

    def _on_box_click(self, widget, event):
        self.button.emit("clicked")
        return True

    def _on_active_window(self, _, event: HyprlandEvent):
        if len(event.data) < 3:
            return

        new_address = "0x" + event.data[2]
        if new_address == self.last_window_address:
            return

        self.last_window_address = new_address

        if self.tray.get_visible():
            self.tray.user_closed = True
            self.tray.hide()
            self.button.set_label("")

    def do_clicked(self, button=None, *args):
        current = self.button.get_label()
        self.button.set_label("" if current == "" else "")

        if self.tray.get_visible():
            self.tray.user_closed = True
            self.tray.hide()
        else:
            self.tray.user_closed = False
            self.tray.show_all()
            self.tray.grab_focus()

        return True
