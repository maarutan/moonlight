from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.centerbox import CenterBox
from .core.config_handler import ConfigHandler
from .core.modules_handler import ModulesHandler
from .modules.corners import NotchedBar


class StatusBar(Window):
    def __init__(self, **kwargs):
        self.confh = ConfigHandler()
        self.modules = ModulesHandler()
        super().__init__(
            title="StatusBar",
            name="StatusBar",
            layer=self.confh.get_layer(),
            all_visible=True,
            visible=True,
            anchor=self.confh.get_position(),
            exclusivity="auto",
            margin=self.confh.get_margin(),
            style_classes="StatusBar",
            style=None,
            **kwargs,
        )

        self.children = [
            CenterBox(
                orientation="h" if self.confh.is_horizontal() else "v",
                start_children=self.modules.modules_start_handler(),
                center_children=self.modules.modules_center_handler(),
                end_children=self.modules.modules_end_handler(),
            ),
            # NotchedBar(self.confh.get_position(), self.confh.get_layer()),
        ]
