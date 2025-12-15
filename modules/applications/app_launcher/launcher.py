from fabric.utils import Gdk, Gtk
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from modules.applications.app_launcher.cli import ALCli
from modules.my_corner.corners import MyCorner
from shared.dropshadow import DropShadow
from utils.widget_utils import setup_keybinds

from .app_window import ALAppWindow
from .tools import ALTools
from .input import ALInput


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
        self.app_window = ALAppWindow(self)
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
                    end_children=self.app_window,
                ),
            ],
        )
        self.tools.toggle("hide")

        setup_keybinds(self.input.entry, "shift tab", self.tools.up)
        setup_keybinds(self.input.entry, "tab", self.tools.down)

        setup_keybinds(self.input.entry, "ctrl j", self.tools.down)
        setup_keybinds(self.input.entry, "ctrl k", self.tools.up)

        self.add(self.main_box)
        ALCli(self)

        self.tools.events()
