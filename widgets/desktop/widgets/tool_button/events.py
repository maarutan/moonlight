from typing import TYPE_CHECKING, Literal
from fabric.utils import GLib, idle_add

from utils.widget_utils import set_cursor_now, setup_cursor_hover


if TYPE_CHECKING:
    from .tool_button import ToolButton


class ButtonEvents:
    def __init__(self, toolbutton: "ToolButton"):
        self.toolbutton = toolbutton
        self._cancel_hide = None
        self._button_hide = False

        setup_cursor_hover(
            self.toolbutton.exp.get_children()[0]
        )  # wrapper inside EventBox

        setup_cursor_hover(self.toolbutton.wrapper.end_container)
        self.toolbutton.wrapper_hover.connect(
            "enter-notify-event",
            lambda w, e: idle_add(lambda: self._on_button_enter(w, e)),
        )
        self.toolbutton.wrapper_hover.connect(
            "leave-notify-event",
            lambda w, e: idle_add(lambda: self._on_button_leave(w, e)),
        )

    def _on_button_enter(self, w, e):
        self.toggle("show")

    def _on_button_leave(self, w, e):
        self.toggle("hide")
        self.toolbutton.exp.expandable_box.close()

    def toggle(self, action: Literal["show", "hide", "auto"] = "auto"):
        show_class = "desktop-edit-button-container-show"
        hide_class = "desktop-edit-button-container-hide"

        timeout = 400
        widget = self.toolbutton.exp.get_children()[0].get_children()[
            0
        ]  # wrapper inside EventBox inside exp

        if action == "auto":
            action = "hide" if not self._is_hidden else "show"

        self._cancel_hide_timeout()

        widget.remove_style_class(show_class)
        widget.remove_style_class(hide_class)

        if action == "show":
            self._is_hidden = False
            widget.add_style_class(show_class)
            self._cancel_hide = idle_add(widget.show)
            setup_cursor_hover(
                self.toolbutton.exp.get_children()[0].get_children()[0]
            )  # wrapper inside EventBox

        elif action == "hide":
            self._is_hidden = True
            self._cancel_hide = GLib.timeout_add(
                300,
                lambda: widget.add_style_class(
                    hide_class
                ),  # time out for expade close animation
            )
            self._cancel_hide = GLib.timeout_add(timeout, widget.hide)

    def _cancel_hide_timeout(self):
        if self._cancel_hide is not None:
            GLib.source_remove(self._cancel_hide)
            self._cancel_hide = None
