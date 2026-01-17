from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.centerbox import CenterBox

from .events import ButtonEvents
from .button_factory import ButtonFactory

if TYPE_CHECKING:
    from ...desktop import Desktop


class ToolButton:
    def __init__(self, desktop: "Desktop"):
        self.desktop = desktop

        self.buttons = ButtonFactory(self)  # create buttons
        self.wrapper = CenterBox(
            size=self.desktop.confh.config["tools"]["hover-size"],
            h_align="center",
            v_align="center",
            style=(
                "background: #222; border-radius: 8px; padding: 8px; "
                "border: 3px solid rgba(255,255,255,0.5);"
                if self.desktop.confh.config["tools"]["preview-hover-zone"]
                else ""
            ),
            center_children=EventBox(
                name="desktop-edit-button-wrapper",
                h_align="center",
                v_align="center",
                v_expand=False,
                h_expand=False,
                child=self.buttons.exp,
            ),
        )
        self.wrapper_hover = EventBox(
            child=EventBox(child=EventBox(child=self.wrapper))
        )
        self.main_box = Box(
            name="desktop-edit-button-container",
            h_align="center",
            v_align="center",
            v_expand=True,
            h_expand=True,
        )

        self.main_box.add(self.wrapper_hover)

        self.desktop.fixed_tools.add(
            self.main_box, anchor=self.desktop.confh.config["tools"]["anchor"]
        )
        self.events = ButtonEvents(self)
