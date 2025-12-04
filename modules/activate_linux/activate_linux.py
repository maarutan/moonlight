from gi.repository import Gtk  # type: ignore
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.label import Label
from fabric.widgets.box import Box

from .config import ActivateLinuxConfig

widget_name = "activate-linux"
confh = ActivateLinuxConfig(widget_name)
enabled = confh.get_option(f"{widget_name}.enabled", True)
if not enabled:
    ActivateLinux = None  # pyright: ignore[reportAssignmentType]
else:

    class ActivateLinux(Window):
        def __init__(self):
            self.confh = confh

            config = self.confh.get_option(f"{widget_name}", {})
            conf_layer = config.get("layer", "")
            conf_anchor = config.get("anchor", "")
            conf_margin = config.get("margin", "0px 0px 0px 0px")

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
                layer=conf_layer,
                anchor=conf_anchor,
                margin=conf_margin,
                child=box,
            )

            if not enabled:
                self.hide()
