from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label

from modules.my_corner.corners import MyCorner
from .tools import DockStationTools
from .config import DockStationConfig
from .servises.hypr import Hypr
from .core.items import DockStationItems
from .core.actions import DockStationActions


widget_name = "dock-station"
confh = DockStationConfig(widget_name)

if not confh.get_option(f"{widget_name}.enabled"):
    DockStation = None  # type: ignore
else:

    class DockStation(Window):
        def __init__(self):
            self.confh = confh
            self.widget_name = widget_name
            self.config = self.confh.get_option(f"{widget_name}")

            self.actions = DockStationActions(self)
            self.tools = DockStationTools(self)
            self.hypr = Hypr(self)
            self.items = DockStationItems(self)

            self.main_box = Box(
                name=f"{widget_name}-box",
                orientation="h" if self.tools.is_horizontal() else "v",
                h_align="center",
                v_align="center",
                h_expand=True,
                v_expand=True,
                children=self.items,
            )

            self.main_event = EventBox(child=EventBox(child=self.main_box))
            self.hover_line = EventBox(name=widget_name + "-hover-line")

            if self.tools.is_horizontal():
                self.hover_line.set_size_request(
                    self.config["hover"]["max-width"], self.config["hover"]["thickness"]
                )
            else:
                self.hover_line.set_size_request(
                    self.config["hover"]["thickness"], self.config["hover"]["max-width"]
                )

            super().__init__(
                name=widget_name,
                anchor=self.config.get("anchor"),
                layer=self.config.get("layer"),
                margin=self.config.get("margin"),
                h_align="center",
                v_align="center",
                h_expand=True,
                v_expand=True,
                child=Box(
                    v_align="fill",
                    h_align="fill",
                    h_expand=True,
                    v_expand=True,
                    orientation="v" if self.tools.is_horizontal() else "h",
                    children=[
                        self.hover_line,
                        self.main_event,
                    ],
                ),
                all_visible=True,
                visible=True,
            )

            if not self.tools.is_horizontal():
                self.add_style_class(widget_name + "-vertical")

            self.tools.auto_hide()  # visible_dock

            self.hover_line.connect("enter-notify-event", self.tools.hover_enter)
            self.hover_line.connect("leave-notify-event", self.tools.hover_leave)

            self.main_event.connect("enter-notify-event", self.tools.hover_enter)
            self.main_event.connect("leave-notify-event", self.tools.hover_leave)
