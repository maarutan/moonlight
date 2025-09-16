from gi.repository import Gtk  # type: ignore
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.label import Label
from fabric.widgets.box import Box


class ActivateLinux(Window):
    def __init__(self, enabled: bool = False):
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
            layer="bottom",
            anchor="bottom right",
            margin="0px 70px 70px 0px",
            child=box,
        )

        if not enabled:
            self.hide()
