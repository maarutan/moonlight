from .core.cava import Cava
from .core.spectrum import Spectrum
from fabric.widgets.overlay import Overlay
from .core.config_handler import CavaladeConfig
from .core.config_parser import ConfParser


class SpectrumRender:
    def __init__(
        self,
        name: str,
        width: int = 980,
        height: int = 100,
        is_horizontal: bool = True,
    ):
        self.confh = CavaladeConfig(name)
        ConfParser(
            config_name=name,
            config_file=self.confh.get_widget_config(),
            section_path=f"cavalade.{name}",
        )
        self.name = name
        self.width = width
        self.height = height
        self.is_horizontal = is_horizontal

        self.cava = Cava(
            class_init=self,
            mainapp=None,
        )

        self.draw = Spectrum(bars=self.cava.bars)

        self.cava.data_handler = self.draw.update

        self.cava.start()

    def get_spectrum_box(self):
        box = Overlay(
            name=self.name,
            h_align="center",
            v_align="center",
        )

        if self.is_horizontal:
            box.set_size_request(self.width, self.height)
        else:
            box.set_size_request(40, 40)

        box.add_overlay(self.draw.area)
        box.show_all()
        return box
