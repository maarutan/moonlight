from fabric.widgets.box import Box
from typing import TYPE_CHECKING
from modules.cavalade.cavalade import SpectrumRender

if TYPE_CHECKING:
    from ..bar import StatusBar


class CavaWidget(Box):
    def __init__(
        self,
        init_class: "StatusBar",
    ):
        self.conf = init_class

        super().__init__(
            name="sb_cava",
            v_expand=True,
            h_expand=True,
            v_align="center",
            h_align="center",
            orientation="h" if self.conf.is_horizontal() else "v",
        )

        self.spectrum_render = SpectrumRender(
            name="status-bar_cava",
            is_horizontal=self.conf.is_horizontal(),
            width=200,
            height=30,
        )

        self.add(self.spectrum_render.get_spectrum_box())
