from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.utils import Gtk

from .config import ConfigHandlerActivateLinux

config_handler = ConfigHandlerActivateLinux()

if not config_handler.config["enabled"]:
    ActivateLinux = None  # pyright: ignore[reportAssignmentType]
else:

    class ActivateLinux(Window):
        def __init__(self):
            self.confh = config_handler

            title = Label(
                name="activate-linux-title",
                label="Activate Linux",
            )
            title.props.hexpand = True  # type: ignore
            title.props.halign = Gtk.Align.FILL  # type: ignore
            title.set_xalign(0.0)

            desc = Label(
                name="activate-linux-desc",
                label="Go to Settings to activate Linux.",
            )
            desc.props.hexpand = True  # type: ignore
            desc.props.halign = Gtk.Align.FILL  # type: ignore
            desc.set_xalign(0.0)

            box = Box(orientation="v", children=[title, desc])

            super().__init__(
                name="activate-linux",
                title="Activate Linux",
                style_classes="activate-linux",
                layer=self.confh.config["layer"],
                anchor=self.confh.config["anchor"],
                margin=self.confh.config["margin"],
                exclusivity="normal",
                child=box,
            )
