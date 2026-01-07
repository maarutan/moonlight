from fabric.widgets.wayland import WaylandWindow
from fabric.widgets.fixed import Fixed


class Desktop(WaylandWindow):
    def __init__(self):
        super().__init__(
            name="desktop",
            anchor="left-top-right-bottom",
            layer="bottom",
            exclusivity="normal",
            style="background: none;",
        )
        self.root = Fixed(
            name="desktop-fixed",
        )
        self.add(self.root)
