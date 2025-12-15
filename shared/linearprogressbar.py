import cairo
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.utils.helpers import clamp
from fabric.utils import Gdk


class LinearProgressBar(CircularProgressBar):
    def do_get_preferred_width(self):
        base = max(200, 2 * self._line_width)
        return (base, base)

    def do_get_preferred_height(self):
        h = max(2 * self._line_width, 10)
        return (h, h)

    def do_draw(self, cr: cairo.Context):
        cr.save()
        state = self.get_state_flags()
        style_context = self.get_style_context()

        border = style_context.get_border(state)
        track_color = style_context.get_color(state)
        progress_color = style_context.get_border_color(state)
        background_color = style_context.get_background_color(state)

        alloc_w = self.get_allocated_width()
        alloc_h = self.get_allocated_height()

        Gdk.cairo_set_source_rgba(cr, background_color)
        cr.rectangle(0, 0, alloc_w, alloc_h)
        cr.fill()

        top_pad = getattr(border, "top", 0)
        bottom_pad = getattr(border, "bottom", 0)
        min_height_prop = style_context.get_property("min-height", state) or 0

        thickness = max(self._line_width, top_pad, bottom_pad, min_height_prop)
        thickness = min(thickness, max(0, alloc_h - (top_pad + bottom_pad)))

        y_center = alloc_h / 2
        cr.set_line_width(thickness)
        cr.set_line_cap(self._line_style)

        track_start = thickness / 2
        track_end = max(track_start, alloc_w - thickness / 2)

        Gdk.cairo_set_source_rgba(cr, track_color)
        cr.move_to(track_start, y_center)
        cr.line_to(track_end, y_center)
        cr.stroke()

        normalized = clamp(
            (self._value - self._min_value) / (self._max_value - self._min_value),
            0.0,
            1.0,
        )
        progress_length = normalized * (track_end - track_start)

        if self._invert:
            start_x = track_end - progress_length
            end_x = track_end
        else:
            start_x = track_start
            end_x = track_start + progress_length

        if end_x > start_x:
            Gdk.cairo_set_source_rgba(cr, progress_color)
            cr.move_to(start_x, y_center)
            cr.line_to(end_x, y_center)
            cr.stroke()

        if child := self.get_child():
            self.propagate_draw(child, cr)

        cr.restore()
        return None
