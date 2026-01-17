from typing import TYPE_CHECKING
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.centerbox import CenterBox

from shared.expandable import Expandable
from .events import ButtonEvents

if TYPE_CHECKING:
    from ...desktop import Desktop


class ToolButton:
    def __init__(self, desktop: "Desktop"):
        self.desktop = desktop

        self.btn = Button(
            name="desktop-edit-button",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            label="Edit",
            on_clicked=lambda *_: desktop.tools.toggle_edit_mode(),
        )
        self.exp = Expandable(
            name="desktop-edit-button-expandable",
            title="tools 󱩼 ",
            widget=Box(children=[self.btn]),
        )

        self.wrapper = CenterBox(
            size=200,
            h_align="center",
            v_align="center",
            center_children=EventBox(
                name="desktop-edit-button-wrapper",
                h_align="center",
                v_align="center",
                v_expand=False,
                h_expand=False,
                child=self.exp,
            ),
        )
        self.wrapper_hover = EventBox(child=EventBox(child=self.wrapper))
        self.main_box = Box(
            name="desktop-edit-button-container",
            h_align="center",
            v_align="center",
            v_expand=True,
            h_expand=True,
        )

        self.main_box.add(self.wrapper_hover)
        self.desktop.fixed_tools.add(self.main_box, anchor="bottom-right")
        ButtonEvents(self)
