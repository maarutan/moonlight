from fabric.widgets.wayland import WaylandWindow
from fabric.widgets.fixed import Fixed as FixedF
from fabric.utils import Gdk
from typing import TYPE_CHECKING, Literal
from utils.widget_utils import setup_cursor_hover
from .tools import DesktopTools
from .widgets.tool_button.tool_button import ToolButton

from .config import ConfigHandlerDesktop
from .core.grid import GridConfig
from .core.gridcell import GridOverlay
from .widgets.label import DesktopWidget
from utils.fixed_tools import FixedTools

from .tools import DesktopTools

config_handler = ConfigHandlerDesktop()

if not config_handler.config["enabled"]:
    Desktop = None  # type: ignore
else:
    if TYPE_CHECKING:

        class Fixed(FixedF):
            def add(self, widget, *args, **kwargs): ...
    else:
        Fixed = FixedF

    class Desktop(WaylandWindow):
        def __init__(self):
            super().__init__(
                name="desktop",
                anchor="left-top-right-bottom",
                layer="bottom",
                exclusivity="normal",
                keyboard_mode="on-demand",
                style="background: none;",
            )
            self.edit_mode = False

            self.root = Fixed(name="desktop-fixed")
            self.fixed_tools = FixedTools(self.root)
            self.tools = DesktopTools(self)
            self.add(self.root)
            self.confh = config_handler

            self.grid = GridConfig(cols=91, rows=51, cell_w=20, cell_h=20, gap=1)

            self.grid_overlay = GridOverlay(self.grid)
            self.root.add(self.grid_overlay)
            self.root.move(self.grid_overlay, 0, 0)
            self.grid_overlay.hide()

            widget = DesktopWidget(self, 40, 40, 1, 1)
            self.root.add(widget)
            self.root.move(widget, widget._grid_x, widget._grid_y)

            ToolButton(self)
