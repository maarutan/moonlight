import math
from gi.repository import Gtk, Gdk, GLib  # type: ignore

from utils.hex_to_rgb import hex_to_rgb
from utils.colors_parse import colors
from utils.widget_utils import setup_cursor_hover


class HamburgerDrawing(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.progress = 0.0
        self.animating = False

        self.set_size_request(40, 40)

        self.connect("draw", self.on_draw)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)  # type: ignore
        self.connect("button-press-event", self.toggle)
        setup_cursor_hover(self)

    def toggle(self, *a):
        if self.animating:
            return
        if self.is_active:
            self.on_deactivate()
        else:
            self.on_activate()

    def on_activate(self):
        self.is_active = True
        self.animating = True
        self.queue_draw()
        GLib.timeout_add(16, self.animate)

    def on_deactivate(self):
        self.is_active = False
        self.animating = True
        self.queue_draw()
        GLib.timeout_add(16, self.animate)

    def animate(self):
        step = 0.08
        if self.is_active:
            self.progress = min(self.progress + step, 1.0)
        else:
            self.progress = max(self.progress - step, 0.0)

        self.queue_draw()

        if (self.is_active and self.progress >= 1.0) or (
            not self.is_active and self.progress <= 0.0
        ):
            self.animating = False
            return False
        return True

    def on_draw(self, widget, cr):
        alloc = self.get_allocation()
        w, h = alloc.width, alloc.height

        bar_w = w * 0.6
        bar_h = 3
        cx, cy = w / 2, h / 2
        spacing = 8

        r, g, b = hex_to_rgb(colors["text"])
        cr.set_source_rgb(r, g, b)
        cr.set_line_width(bar_h)
        cr.set_line_cap(1)

        t = self.progress
        angle = t * (math.pi / 4)
        offset = spacing * (1 - t)

        cr.save()
        cr.translate(cx, cy - offset)
        cr.rotate(angle)
        cr.move_to(-bar_w / 2, 0)
        cr.line_to(bar_w / 2, 0)
        cr.stroke()
        cr.restore()

        cr.save()
        cr.translate(cx, cy + offset)
        cr.rotate(-angle)
        cr.move_to(-bar_w / 2, 0)
        cr.line_to(bar_w / 2, 0)
        cr.stroke()
        cr.restore()

        if t < 0.9:
            cr.save()
            cr.translate(cx, cy)
            alpha = 1 - t / 0.9
            cr.set_source_rgba(1, 1, 1, alpha)
            cr.move_to(-bar_w / 2, 0)
            cr.line_to(bar_w / 2, 0)
            cr.stroke()
            cr.restore()
