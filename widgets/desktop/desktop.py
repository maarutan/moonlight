from fabric.widgets.wayland import WaylandWindow


class Desktop(WaylandWindow):
    def __init__(self):
        super().__init__(
            name="desktop",
            anchor="left-top-right-bottom",
            layer="bottom",
            exclusivity="normal",
        )
