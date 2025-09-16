import math
from gi.repository import Gtk, Gdk, GLib  # type: ignore


class HamburgerDrawing(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.progress = 0.0
        self.animating = False

        self.set_size_request(40, 40)

        self.connect("draw", self.on_draw)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.toggle)

    def toggle(self, *a):
        self.is_active = not self.is_active
        self.animating = True
        GLib.timeout_add(16, self.animate)
        return True

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

        cr.set_source_rgb(1, 1, 1)
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
