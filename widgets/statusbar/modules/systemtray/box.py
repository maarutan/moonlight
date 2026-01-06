from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.centerbox import CenterBox
from fabric.utils.helpers import GLib

from typing import TYPE_CHECKING, Literal
from utils.widget_utils import (
    setup_cursor_hover,
    bar_margin_handler,
    bar_anchor_handler,
    event_close_popup,
)

if TYPE_CHECKING:
    from ...config import ConfigHandlerStatusBar
    from .button import SystemTrayButton

from .items import SystemTrayItems


class SystemTrayBox(Window):
    def __init__(
        self,
        class_button: "SystemTrayButton",
        statusbar_config: "ConfigHandlerStatusBar",
        columns: int = 5,
        icon_size: int = 24,
    ):
        self.confh = statusbar_config
        self.conf_button = class_button
        self.col = columns
        self.icon_size = icon_size

        self.is_open = False
        self._hide_timer = None

        main_box = self.build()

        super().__init__(
            name="statusbar-system-tray",
            exclusivity="none",
            anchor=self.anchor_handler(),
            margin=self.margin_handler(),
            keyboard_mode="on-demand",
            child=main_box,
        )
        self.add_keybinding("Escape", lambda: self.toggle("hide"))

    def build(self) -> Box:
        self.main_box = Box(name="statusbar-system-tray-box", orientation="v")

        title = Label(name="statusbar-system-tray-title", label="System Tray")
        close = Button(
            name="statusbar-system-tray-close",
            label="",
            on_clicked=lambda *_: self.toggle("hide"),
        )
        setup_cursor_hover(close)

        header = CenterBox(
            name="statusbar-system-tray-header",
            orientation="h",
            start_children=title,
            end_children=close,
        )

        event_close_popup(lambda: self.toggle("hide"))

        self.main_box.children = [
            header,
            SystemTrayItems(
                statusbar_config=self.confh,
                is_exist_popup=True,
                columns=self.col,
                icon_size=self.icon_size,
            ),
        ]

        return self.main_box

    def toggle(self, action: Literal["show", "hide", "auto"] = "auto"):
        show_class = "popup-show"
        hide_class = "popup-hide"

        self.main_box.remove_style_class(show_class)
        self.main_box.remove_style_class(hide_class)

        if self._hide_timer:
            GLib.source_remove(self._hide_timer)
            self._hide_timer = None

        def finish_show():
            self.main_box.remove_style_class(show_class)
            self._hide_timer = None

        def finish_hide():
            self.main_box.remove_style_class(hide_class)
            self._hide_timer = None
            self.hide()

        def show():
            self.show()
            self.is_open = True
            self.main_box.add_style_class(show_class)
            self._hide_timer = GLib.timeout_add(200, finish_show)

        def hide():
            self.is_open = False
            self.main_box.add_style_class(hide_class)
            self._hide_timer = GLib.timeout_add(200, finish_hide)

        match action:
            case "show":
                show()
                self.conf_button.arrow.open()
            case "hide":
                hide()
                self.conf_button.arrow.close()
            case "auto":
                hide() if self.is_open else show()

    def margin_handler(self) -> str:
        return bar_margin_handler(
            position=self.confh.config["position"],
            layout_config=self.confh.config["layout"],
            default_value=30,
            widget_name="systemtray",
            px=40,
        )

    def anchor_handler(self) -> str:
        return bar_anchor_handler(
            position=self.confh.config["position"],
            layout_config=self.confh.config["layout"],
            default_value="top-right",
            widget_name="systemtray",
        )
