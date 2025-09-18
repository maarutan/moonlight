from fabric.widgets.stack import Stack
from fabric.widgets.wayland import WaylandWindow as Window
from .cavalade.cavalade import SpectrumRender
from gi.repository import GLib  # type: ignore
from config import CAVA_APP_DIR


class CavaDesktop(Window):
    def __init__(self):
        self.default_bar = 600

        self.cava_render = SpectrumRender(
            name="desktop-cava-render",
            config_dir=CAVA_APP_DIR,
            config_file=CAVA_APP_DIR / "desktop_cava.json",
        )
        self.spectrum_box = self.cava_render.get_spectrum_box()
        self.spectrum_box.show_all()

        super().__init__(
            name="desktop-cava",
            anchor="bottom left",
            layer="bottom",
            h_align="start",
            v_align="start",
        )

        box = Stack(name="desktop-cava-stack", children=self.spectrum_box)
        box.show_all()
        self.add(box)
