from fabric.widgets.widget import Widget
from fabric.utils.helpers import Gtk
from utils.widget_utils import setup_cursor_hover
from loguru import logger


class Switch(Gtk.Switch, Widget):  # pyright: ignore[reportIncompatibleVariableOverride]
    def __init__(
        self,
        active: bool = False,
        name: str | None = None,
        visible: bool = True,
        all_visible: bool = False,
        style: str | None = None,
        style_classes: str | None = None,
        tooltip_text: str | None = None,
        tooltip_markup: str | None = None,
        h_align=None,
        v_align=None,
        h_expand: bool = False,
        v_expand: bool = False,
        size=None,
        **kwargs,
    ):
        default_style = "Switch"
        Gtk.Switch.__init__(self)
        Widget.__init__(
            self,
            default_style,
            visible,
            all_visible,
            style,
            style_classes,
            tooltip_text,
            tooltip_markup,
            h_align,
            v_align,
            h_expand,
            v_expand,
            size,
            **kwargs,
        )

        self.set_active(active)
        self.set_halign(Gtk.Align.START)
        self.set_hexpand(False)
        self.set_valign(Gtk.Align.CENTER)
        self.set_name(name or default_style)
        setup_cursor_hover(self)

    def connect_changed(self, callback):
        if callback is not None:
            self.connect("state-set", lambda w, state: callback(state))
        else:
            logger.warning("connect_changed called with None callback")
