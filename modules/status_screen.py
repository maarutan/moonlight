from fabric.widgets.label import Label
from fabric.widgets.wayland import WaylandWindow as Window


class StatusScreen(Window):
    def __init__(self):
        self.memory = Label(name="memory", label="")
