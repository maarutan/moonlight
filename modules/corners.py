from fabric.widgets.shapes import Corner
from typing import Literal
from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window
from .status_bar.core._config_handler import ConfigHandler


class MyCorner(Box):
    def __init__(
        self,
        corner: Literal["top-left", "top-right", "bottom-left", "bottom-right"],
        orientation_pos: bool = True,
    ):
        super().__init__(
            style="margin-bottom: 15px;",
            orientation="v" if orientation_pos else "h",
            name="corner-container",
            children=Corner(
                name="corner",
                orientation=corner,
                h_expand=False,
                v_expand=False,
                h_align="center",
                v_align="center",
                size=40,
            ),
        )


class ScreenCorners(Window):
    def __init__(self, orientation_pos: bool = True):
        self.confh = ConfigHandler()
        super().__init__(
            layer="top",
            anchor="top left bottom right",
            style="background: transparent;",
            exclusivity=self.exclusivity_handler(),
            # exclusivity="",
            pass_through=True,
            child=Box(
                orientation="v" if orientation_pos else "h",
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
            name="corner-container",
            children=Corner(
                name="corner",
                orientation=orientation,
                h_expand=False,
                v_expand=False,
                h_align="center",
                v_align="center",
                size=37,
            ),
        )

    def exclusivity_handler(self) -> Literal["normal", "none"]:
        bar_margin = " ".join(self.confh.get_margin().strip().split())

        if bar_margin in ("0px 0px 0px 0px", "0 0 0 0"):
            return "none"
        return "normal"
