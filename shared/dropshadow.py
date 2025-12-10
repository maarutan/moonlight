from typing import Literal
from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window


class DropShadow(Window):
    def __init__(self):
        super().__init__(
            name="drop-shadow",
            layer="top",
            anchor="top-left-right-bottom",
        )
        self.is_hidden = True
        self.box = Box(name="drop-shadow-box")
        self.add(self.box)
        self.hide()

    def toggle(self, action: Literal["show", "hide", "auto"] = "auto"):
        class_show = "drop-shadow-show"
        class_hide = "drop-shadow-hide"

        self.box.remove_style_class(class_show)
        self.box.remove_style_class(class_hide)

        if action == "auto":
            action = "show" if self.is_hidden else "hide"

        if action == "show":
            self.is_hidden = False
            self.show_all()
            self.box.add_style_class(class_show)

        elif action == "hide":
            self.is_hidden = True
            self.box.add_style_class(class_hide)
            self.hide()
