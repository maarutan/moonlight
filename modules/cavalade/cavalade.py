from pathlib import Path
from fabric.widgets.overlay import Overlay
from .core.cava import Cava
from .core.spectrum import Spectrum


class SpectrumRender:
    def __init__(
        self,
        config_file: str | Path,
        config_dir: str | Path,
        width: int = 980,
        height: int = 100,
        name: str = "cavalade",
        is_horizontal: bool = True,
    ):
        self.name = name
        self.width = width
        self.height = height
        self.config_dir = config_dir
        self.config_file = config_file
        self.is_horizontal = is_horizontal

        # создаём cava без data_handler
        self.cava = Cava(
            name=self.name,
            config_file=self.config_file,
            config_dir=self.config_dir,
            mainapp=None,
        )

        # создаём Spectrum
        self.draw = Spectrum(bars=self.cava.bars)

        # теперь назначаем обработчик
        self.cava.data_handler = self.draw.update

        # запускаем cava
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
