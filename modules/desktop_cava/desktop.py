from fabric.widgets.stack import Stack
from fabric.widgets.wayland import WaylandWindow as Window
from .cava import SpectrumRender
from gi.repository import GLib  # type: ignore


class CavaDesktop(Window):
    def __init__(self):
        self.default_bar = 600

        # создаём рендер
        self.cava_render = SpectrumRender(True)
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
