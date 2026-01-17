from typing import TYPE_CHECKING, Literal
from fabric.utils import GLib

if TYPE_CHECKING:
    from .tool_button import ToolButton


class ButtonEvents:
    def __init__(self, toolbutton: "ToolButton"):
        self.toolbutton = toolbutton

        self._cancel_hide_ids: list[int] = []
        self._is_hidden = False

        self.widget = self.toolbutton.buttons.exp.get_children()[0].get_children()[0]

        self.toggle("hide")

        self.toolbutton.wrapper_hover.connect(
            "enter-notify-event",
            lambda w, e: GLib.idle_add(self._on_button_enter, w, e),
        )
        self.toolbutton.wrapper_hover.connect(
            "leave-notify-event",
            lambda w, e: GLib.idle_add(self._on_button_leave, w, e),
        )

    def _on_button_enter(self, w, e):
        self.toggle("show")
        return False

    def _on_button_leave(self, w, e):
        self.toggle("hide")
        try:
            self.toolbutton.buttons.exp.expandable_box.close()
        except Exception:
            pass
        return False

    def toggle(self, action: Literal["show", "hide", "auto"] = "auto"):
        show_class = "desktop-edit-button-container-show"
        hide_class = "desktop-edit-button-container-hide"
        timeout = 500

        if action == "auto":
            action = "show" if self._is_hidden else "hide"

        self._cancel_hide_timeout()

        try:
            self.widget.remove_style_class(show_class)
            self.widget.remove_style_class(hide_class)
        except AttributeError:
            pass

        if action == "show":
            self._is_hidden = False
            try:
                self.widget.add_style_class(show_class)
            except AttributeError:
                pass

            sid = GLib.idle_add(self.widget.show)
            self._cancel_hide_ids.append(sid)

        elif action == "hide":
            self._is_hidden = True

            sid1 = GLib.timeout_add(
                300,
                lambda: (getattr(self.widget, "add_style_class")(hide_class) or False),
            )
            self._cancel_hide_ids.append(sid1)

            sid2 = GLib.timeout_add(timeout, lambda: (self.widget.hide() or False))
            self._cancel_hide_ids.append(sid2)

    def _cancel_hide_timeout(self):
        for sid in self._cancel_hide_ids:
            try:
                GLib.source_remove(sid)
            except Exception:
                pass
        self._cancel_hide_ids.clear()
