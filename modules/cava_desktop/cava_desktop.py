from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.stack import Stack

from ..cavalade.cavalade import SpectrumRender
from .config import CavaDesktopConfig

widget_name = "cava_desktop"
confh = CavaDesktopConfig(widget_name)

cavalade = SpectrumRender(
    name=widget_name,
    height=200,
    width=1000,
)

enabled = confh.get_option(f"{widget_name}.enabled", True)

if not enabled:
    CavaDesktop = None  # pyright: ignore[reportAssignmentType]
else:

    class CavaDesktop(Window):
        def __init__(self):
            self.conf = confh
            config = confh.get_option(f"{widget_name}")
            super().__init__(
                name="cava_desktop",
                anchor=config.get("anchor", ""),
                layer=config.get("layer", ""),
                margin=config.get("margin", ""),
                exclusivity="none",
                h_align="center",
                v_align="center",
                h_expand=True,
                style="background: none;",
            )

            self.stack = Stack()
            self.stack.add(cavalade.get_spectrum_box())

            self.show_all()
            self.add(self.stack)
