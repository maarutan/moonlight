import gi
import cairo
from typing import Literal, Iterable
from fabric.core.service import Property
from fabric.widgets.container import Container
from fabric.utils.helpers import get_enum_member, clamp

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk


class LinearProgressBar(Gtk.Bin, Container):
    @Property(float, "read-write", default_value=0.0)
    def min_value(self) -> float:
        return self._min_value

    @min_value.setter
    def min_value(self, value: float):
        self._min_value = clamp(value, value, self.max_value)
        return self.queue_draw()

    @Property(float, "read-write", default_value=1.0)
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, value: float):
        if value == 0:
            raise ValueError("max_value cannot be zero")
        self._max_value = value
        return self.queue_draw()

    @Property(float, "read-write", default_value=1.0)
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float):
        self._value = clamp(value, self.min_value, self.max_value)
        return self.queue_draw()

    @Property(int, "read-write", default_value=4)
    def line_width(self) -> int:
        return self._line_width

    @line_width.setter
    def line_width(self, value: int):
        self._line_width = value
        return self.queue_draw()

    @Property(object, "read-write")
    def line_style(self) -> cairo.LineCap:
        return self._line_style

    @line_style.setter
    def line_style(
        self,
        line_style: Literal["none", "butt", "round", "square"] | cairo.LineCap,
    ):
        self._line_style = get_enum_member(cairo.LineCap, line_style)
        return self.queue_draw()

    def __init__(
        self,
        value: float = 1.0,
        min_value: float = 0.0,
        max_value: float = 1.0,
        line_width: int = 4,
        line_style: Literal["none", "butt", "round", "square"]
        | cairo.LineCap = cairo.LineCap.BUTT,
        child: Gtk.Widget | None = None,
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
    ):
        Gtk.DrawingArea.__init__(self)  # type: ignore
        Container.__init__(
            self,
            child,
            name,
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
        self._value = value
        self._min_value = min_value
        self._max_value = max_value
        self._line_width = line_width
        self._line_style = get_enum_member(cairo.LineCap, line_style)
        self.connect("draw", self.do_draw)

    def do_get_preferred_width(self):
        return 100, 200

    def do_get_preferred_height(self):
        return 10, 10 + self._line_width

    def do_draw(self, cr: cairo.Context):
        state = self.get_state_flags()
        style_context = self.get_style_context()

        border = style_context.get_border(state)  # type: ignore
        track_color = style_context.get_background_color(state)  # type: ignore
        progress_color = style_context.get_color(state)  # type: ignore

        width = self.get_allocated_width()
        height = self.get_allocated_height()

        cr.set_line_cap(self._line_style)
        cr.set_line_width(self._line_width)

        # Draw track
        Gdk.cairo_set_source_rgba(cr, track_color)  # type: ignore
        cr.rectangle(0, height / 2 - self._line_width / 2, width, self._line_width)
        cr.fill()

        # Draw progress
        normalized_value = clamp(
            (self._value - self._min_value) / (self._max_value - self._min_value),
            0.0,
            1.0,
        )
        progress_width = normalized_value * width

        Gdk.cairo_set_source_rgba(cr, progress_color)  # type: ignore
        cr.rectangle(
            0, height / 2 - self._line_width / 2, progress_width, self._line_width
        )
        cr.fill()

        if child := self.get_child():
            self.propagate_draw(child, cr)

        return False
