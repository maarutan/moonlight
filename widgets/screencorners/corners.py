from typing import Literal
from fabric.widgets.box import Box
from fabric.widgets.shapes import Corner
from fabric.widgets.wayland import WaylandWindow as Window
from .config import ConfigHandlerScreenCorners

config_handler = ConfigHandlerScreenCorners()

if not config_handler.config["enabled"]:
    ScreenCorners = None  # pyright: ignore[reportAssignmentType]
else:

    class ScreenCorners(Window):
        def __init__(self):
            self.confh = config_handler

            super().__init__(
                name="screen-corners",
                style_classes="screen-corners",
                layer="top",
                anchor="top left bottom right",
                exclusivity=self.exclusivity_handler(),
                style="background: none;",
                pass_through=True,
                child=Box(
                    orientation="v",
                    children=[
                        Box(
                            children=[
                                self.make_corner("top-left"),
                                Box(h_expand=True),
                                self.make_corner("top-right"),
                            ]
                        ),
                        Box(v_expand=True),
                        Box(
                            children=[
                                self.make_corner("bottom-left"),
                                Box(h_expand=True),
                                self.make_corner("bottom-right"),
                            ]
                        ),
                    ],
                ),
            )

        def make_corner(self, orientation) -> Box:
            return Box(
                h_expand=False,
                v_expand=False,
                children=Corner(
                    name="corner",
                    orientation=orientation,
                    h_expand=False,
                    v_expand=False,
                    h_align="center",
                    v_align="center",
                    size=self.confh.config["size"],
                ),
            )

        def exclusivity_handler(self) -> Literal["normal", "none"]:
            transparent = self.confh.config_statusbar["transparent"]

            try:
                margins = [
                    int(v.replace("px", "").strip())
                    for v in self.confh.config_statusbar["margin"].split()
                ]
            except ValueError:
                margins = [0, 0, 0, 0]

            has_nonzero_margin = any(v > 0 for v in margins)

            if transparent or has_nonzero_margin:
                return "normal"
            return "none"
