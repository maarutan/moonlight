from fabric.widgets.wayland import WaylandWindow as Window


class Dock(Window):
    def __init__(self):
        super().__init__(
            name="dock-station",
            layer="bottom",
            anchor="bottom center",
            exclusivity="none",
        )
