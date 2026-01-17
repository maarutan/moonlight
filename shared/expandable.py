from utils.widget_utils import set_cursor_now, setup_cursor_hover
from typing import Iterable, Literal
from fabric.core.service import Property
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label
from fabric.widgets.revealer import Revealer
from fabric.widgets.button import Button
from fabric.utils.helpers import Gtk
from .arrow_icon import ArrowIcon


class CollapsibleBox(Box):
    @Property(bool, "read-write", default_value=False)
    def expanded(self) -> bool:  # type: ignore
        return self._revealer.child_revealed

    @expanded.setter
    def expanded(self, value: bool):
        if value:
            self._revealer.reveal()
            self._arrow_icon.animate_to(90.0)
        else:
            self._revealer.unreveal()
            self._arrow_icon.animate_to(0.0)

    def __init__(
        self,
        title: str,
        child: Gtk.Widget | None = None,
        expanded: bool = False,
        spacing: int = 0,
        orientation: Literal["horizontal", "vertical", "h", "v"]
        | Gtk.Orientation = Gtk.Orientation.VERTICAL,
        name: str | None = None,
        visible: bool = True,
        all_visible: bool = False,
        style: str | None = None,
        style_classes: Iterable[str] | str | None = None,
        tooltip_text: str | None = None,
        tooltip_markup: str | None = None,
        h_align: Literal["fill", "start", "end", "center", "baseline"]
        | Gtk.Align
        | None = None,
        v_align: Literal["fill", "start", "end", "center", "baseline"]
        | Gtk.Align
        | None = None,
        h_expand: bool = False,
        v_expand: bool = False,
        size: Iterable[int] | int | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            spacing=spacing,
            orientation=orientation,
            children=None,
            name=name,
            visible=visible,
            all_visible=all_visible,
            style=style,
            style_classes=style_classes,
            tooltip_text=tooltip_text,
            tooltip_markup=tooltip_markup,
            h_align=h_align,
            v_align=v_align,
            h_expand=h_expand,
            v_expand=v_expand,
            size=size,
            **kwargs,
        )

        ctx = self.get_style_context()
        ctx.add_class("collapsible-box")

        #
        # === HEADER ===
        #
        self._header_box = Box(
            orientation="h",
            spacing=6,
            h_align="fill",
            v_align="center",
            h_expand=True,
            v_expand=False,
        )

        self._arrow_icon = ArrowIcon(size=14, angle_deg=(90.0 if expanded else 0.0))

        self._title_label = Label(
            label=title,
            h_align="start",
            v_align="center",
        )

        self._header_box.pack_start(self._arrow_icon, False, False, 0)
        self._header_box.pack_start(self._title_label, True, True, 0)

        self._header_button = Button(
            name=f"{name}-header-button",
            h_align="fill",
            v_align="center",
            h_expand=True,
            v_expand=False,
            child=self._header_box,
        )

        setup_cursor_hover(self._header_button)
        self._header_button.connect("clicked", self._on_header_clicked)

        #
        # === BODY / REVEALER ===
        #
        self._revealer = Revealer(
            child=child,
            child_revealed=expanded,
            transition_type="slide-down",
            transition_duration=250,
        )

        #
        # === BUILD STRUCTURE ===
        #
        self.pack_start(self._header_button, False, False, 0)
        self.pack_start(self._revealer, False, False, 0)

    #
    # === SIGNAL HANDLERS ===
    #

    def _on_header_clicked(self, _btn):
        now_expanded = self._revealer.child_revealed
        if now_expanded:
            self._revealer.unreveal()
            self._arrow_icon.animate_to(0.0)
        else:
            self._revealer.reveal()
            self._arrow_icon.animate_to(90.0)

    #
    # === API ===
    #

    def toggle(self):
        self.expanded = not self.expanded

    def set_child(self, widget: Gtk.Widget | None):
        self._revealer.child = widget

    def close(self):
        self.expanded = False

    def open(self):
        self.expanded = True


class Expandable(Box):
    def __init__(
        self,
        name: str,
        title: str,
        widget: Box,
    ):
        self.body = EventBox(child=EventBox(child=widget))
        self.expandable_box = CollapsibleBox(
            title=title,
            name=name,
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            child=self.body,
        )

        super().__init__(
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            children=EventBox(child=self.expandable_box),
        )
