from fabric.widgets.label import Label
from fabric.widgets.eventbox import EventBox
from .events import WidgetParentEvents


class DesktopWidget(EventBox):
    def __init__(self, desktop, gx, gy, gw=1, gh=1):
        super().__init__()

        self.desktop = desktop
        self.gx, self.gy = gx, gy
        self.gw, self.gh = gw, gh
        self.dragging = False

        self.content = Label(
            label="Widget",
            style="background: #222; border-radius: 8px; padding: 8px;",
        )
        self.add(self.content)

        x, y = desktop.grid.cell_to_px(gx, gy)
        w, h = desktop.grid.size_px(gw, gh)
        self.set_size_request(w, h)
        self._grid_x = x
        self._grid_y = y

        self.events = WidgetParentEvents(self)

    def show_border(self):
        self.content.set_style(
            "background: #222;"
            "border-radius: 8px;"
            "padding: 8px;"
            "border: 3px solid rgba(255,255,255,0.5);"
        )

    def hide_border(self):
        self.content.set_style(
            "background: #222; border-radius: 8px; padding: 8px; border: none;"
            "margin:0px;"
        )
