from fabric.widgets.shapes import Corner
from typing import Literal
from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window
from .status_bar.core._config_handler import ConfigHandlerStatusBar


class MyCorner(Box):
    def __init__(
        self,
        corner: Literal["top-left", "top-right", "bottom-left", "bottom-right"],
        name: str = "corner-container",
        orientation_pos: bool = True,
    ):
        super().__init__(
            # style="margin-bottom: 15px;",
            orientation="v" if orientation_pos else "h",
            name=name,
            children=Corner(
                name="corner",
                orientation=corner,
                h_expand=False,
                v_expand=False,
                h_align="center",
                v_align="center",
                size=32,
            ),
        )


class ScreenCorners(Window):
    def __init__(self, is_horizontal: bool = True):
        self.cfg = ConfigHandlerStatusBar()
        super().__init__(
            name="screen-corners",
            style_classes="screen-corners",
            layer="top",
            anchor="top left bottom right",
            # style="",
            exclusivity=self.exclusivity_handler(),
            pass_through=True,
            child=Box(
                orientation="v" if is_horizontal else "h",
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
                size=32,
            ),
        )

    def exclusivity_handler(self) -> Literal["normal", "none"]:
        bar_margin = " ".join(self.cfg.bar.margin().strip().split())

        if bar_margin in ("0px 0px 0px 0px", "0 0 0 0"):
            return "none"
        return "normal"
