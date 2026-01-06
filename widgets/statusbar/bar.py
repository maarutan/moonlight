from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow
from fabric.widgets.label import Label

from .config import ConfigHandlerStatusBar
from .core.module_handling import ModuleManager

config_handler = ConfigHandlerStatusBar()

if not config_handler.config["enabled"]:
    StatusBar = None  # pyright: ignore [reportAssignmentType]
else:

    class StatusBar(WaylandWindow):
        def __init__(self):
            self.confh = config_handler
            self.modules = ModuleManager(self)

            super().__init__(
                name="statusbar",
                layer="top",
                anchor=self.confh.anchor(),
                exclusivity="auto",
                style="background:none;" if self.confh.config["transparent"] else "",
                margin=self.confh.config["margin"],
                child=CenterBox(
                    name="statusbar-layouts",
                    orientation=self.confh.orientation,  # type: ignore
                    start_children=self.modules.start_modules(),
                    center_children=self.modules.center_modules(),
                    end_children=self.modules.end_modules(),
                ),
                style_classes="statusbar-vertical"
                if self.confh.orientation == "v"
                else "",
            )
