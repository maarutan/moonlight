from fabric.widgets.button import Button
from utils.widget_utils import setup_cursor_hover
from typing import TYPE_CHECKING
from shared.arrow_icon import ArrowIconTwo

if TYPE_CHECKING:
    from ...bar import StatusBar

from .box import SystemTrayBox


class SystemTrayButton(Button):
    def __init__(
        self,
        class_init: "StatusBar",
        columns: int = 4,
        icon_size: int = 32,
        button_size: int = 24,
    ):
        self.conf = class_init

        self.arrow = ArrowIconTwo(button_size)
        self.popup = SystemTrayBox(
            class_button=self,
            class_init=self.conf,
            columns=columns,
            icon_size=icon_size,
        )

        super().__init__(
            name="sb_system-tray-button",
            on_clicked=self.on_click,
        )
        if not self.conf.is_horizontal():
            self.add_style_class("sb_system-tray-button-vertical")

        setup_cursor_hover(self)
        self.add(self.arrow)

        self.popup.hide()

    def on_click(self, *_):
        if self.popup.is_open:
            self.popup.toggle("hide")
        else:
            self.popup.toggle("show")
