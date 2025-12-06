from fabric.utils import idle_add
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from modules.my_corner.corners import MyCorner
from shared.dropshadow import DropShadow
from .tools import ALTools
from .input import ALInput
from .app_window import ALAppWindow


class AppLauncher(Window):
    def __init__(self):
        super().__init__(
            name="app_launcher",
            anchor="center left",
            layer="overlay",
            exclusivity="none",
            keyboard_mode="on-demand",
        )

        self.tools = ALTools(self)
        self.input = ALInput()
        self.shadow = DropShadow()
        self.main_box = Box(
            name="al_box",
            orientation="v",
            h_align="center",
            h_expand=False,
            children=[
                CenterBox(start_children=MyCorner("bottom-left")),
                self.input,
                CenterBox(
                    h_expand=True,
                    start_children=MyCorner("top-left"),
                    end_children=ALAppWindow(self),
                ),
            ],
        )

        self.show_all()
        self.tools.events()

        self.shadow.show()
        self.add(self.main_box)
