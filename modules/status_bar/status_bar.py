from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.centerbox import CenterBox

from ..corners import MyCorner
from .core.config_handler import ConfigHandler
from .core.modules_handler import ModulesHandler


class StatusBar(Window):
    def __init__(self, **kwargs):
        self.confh = ConfigHandler()
        self.modules = ModulesHandler()
        self.bar_content = CenterBox(
            name="center-bar",
            orientation="h" if self.confh.is_horizontal() else "v",
        )

        self.bar_content.start_children = [
            self.modules.modules_start_handler(),
            # MyCorner("top-left", self.confh.is_horizontal()),
        ]
        self.bar_content.center_children = [
            # MyCorner("top-right", self.confh.is_horizontal()),
            self.modules.modules_center_handler(),
            # MyCorner("top-left", self.confh.is_horizontal()),
        ]
        self.bar_content.end_children = [
            # MyCorner("top-right", self.confh.is_horizontal()),
            self.modules.modules_end_handler(),
        ]

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
            child=self.bar_content,
            **kwargs,
        )
