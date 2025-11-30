from fabric.widgets.shapes import Corner
from typing import Literal
from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window
from .config import MyCornerConfig
# from .status_bar.core._config_handler import ConfigHandlerStatusBar


widget_name = "my-corner"
confh = MyCornerConfig(widget_name)
enabled = confh.get_option(f"{widget_name}.enabled", True)

if not confh.get_option(f"{widget_name}.my_corner.enabled", True):
    MyCorner = None  # pyright: ignore[reportAssignmentType]
else:

    class MyCorner(Box):
        def __init__(
            self,
            corner: Literal["top-left", "top-right", "bottom-left", "bottom-right"],
            name: str = "corner-container",
        ):
            super().__init__(
                # style="margin-bottom: 15px;",
                orientation="v",
                name=name,
                children=Corner(
                    name="corner",
                    orientation=corner,
                    h_expand=False,
                    v_expand=False,
                    h_align="center",
                    v_align="center",
                    size=confh.get_option(f"{widget_name}.my_corner.size", 40),
                ),
            )


if not enabled:
    ScreenCorners = None  # pyright: ignore[reportAssignmentType]
else:

    class ScreenCorners(Window):
        def __init__(self, enabled: bool = True):
            self.cfg = confh

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

            if not enabled:
                self.hide()

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
                    size=confh.get_option(f"{widget_name}.screen_corner.size", 40),
                ),
            )

        def exclusivity_handler(self) -> Literal["normal", "none"]:
            conf = confh.confbar
            name = confh.bar_wideget_name

            margin_raw = conf.get_option(f"{name}.margin", "0px 0px 0px 0px")
            transparent = conf.get_option(f"{name}.transparent", False)

            try:
                margins = [int(v.replace("px", "").strip()) for v in margin_raw.split()]
            except ValueError:
                margins = [0, 0, 0, 0]

            has_nonzero_margin = any(v > 0 for v in margins)

            if transparent or has_nonzero_margin:
                return "normal"
            return "none"
