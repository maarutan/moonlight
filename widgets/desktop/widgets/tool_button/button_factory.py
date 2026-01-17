from typing import TYPE_CHECKING, Callable
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from shared.expandable import Expandable
from utils.widget_utils import setup_cursor_hover


if TYPE_CHECKING:
    from .tool_button import ToolButton


class ButtonFactory:
    def __init__(self, toolbutton: "ToolButton"):
        self.toolbutton = toolbutton
        self.btn = self._make_buttons(
            label="Edit",
            name="desktop-edit-button",
            on_clicked=lambda *_: toolbutton.desktop.tools.toggle_edit_mode(),
        )

        self.exp = Expandable(
            name="desktop-edit-button-expandable",
            title=self.toolbutton.desktop.confh.config["tools"]["title"],
            widget=Box(children=[self.btn]),
        )

    def _make_buttons(
        self,
        name: str,
        label: str,
        on_clicked: Callable,
        h_align: str = "fill",
        v_align: str = "fill",
        h_expand: bool = True,
        v_expand: bool = True,
    ) -> Button:
        btn = Button(
            name=name,
            h_align=h_align,  # type: ignore
            v_align=v_align,  # type: ignore
            h_expand=h_expand,
            v_expand=v_expand,
            label=label,
            on_clicked=on_clicked,
        )
        setup_cursor_hover(btn)
        return btn
