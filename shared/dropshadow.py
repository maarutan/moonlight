from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window


class DropShadow(Window):
    def __init__(self):
        super().__init__(
            name="drop-shadow",
            layer="top",
            anchor="top-left-right-bottom",
        )
        box = Box(
            name="drop-shadow-box",
            style="opacity: 0.5;",
        )
        self.show_all()
        self.add(box)
