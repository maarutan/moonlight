from fabric.utils.helpers import idle_add
from fabric.widgets.button import Button
from utils.widget_utils import setup_cursor_hover
from typing import TYPE_CHECKING
from shared.arrow_icon import ArrowIconTwo

if TYPE_CHECKING:
    from .systemtray import SystemTrayWidget

from .box import SystemTrayBox


class SystemTrayButton(Button):
    def __init__(self, systemtray: "SystemTrayWidget"):
        self.systemtray = systemtray

        super().__init__(
            name="statusbar-system-tray-button",
            on_clicked=self.on_click,
        )

        self.arrow = ArrowIconTwo(
            size=int(self.systemtray.config["collapse"]["button-size"])
        )

        self.popup = SystemTrayBox(self)

        if self.systemtray.confh.is_vertical():
            self.add_style_class("statusbar-system-tray-button-vertical")

        setup_cursor_hover(self)
        self.add(self.arrow)

        idle_add(self.popup.hide)

    def on_click(self, *_):
        if self.popup.is_open:
            self.popup.toggle("hide")
        else:
            self.popup.toggle("show")
