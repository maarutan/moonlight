import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GObject, cairo
import math


class ArrowButton(Gtk.EventBox):
    def __init__(self, size=24):
        super().__init__()
        self.set_size_request(size, size)
        self.size = size
        self.angle = 0
        self.target_angle = 0
        self.animation_speed = 0.1

        self.darea = Gtk.DrawingArea()
        self.add(self.darea)
        self.darea.connect("draw", self.on_draw)

        self.connect("button-press-event", self.on_click)

        GLib.timeout_add(16, self.animate)  # ~60 FPS

    def on_click(self, widget, event):
        if self.target_angle == 0:
            self.target_angle = math.pi  # вниз
        else:
            self.target_angle = 0  # вверх
        return True

    def animate(self):
        diff = self.target_angle - self.angle
        if abs(diff) < 0.01:
            self.angle = self.target_angle
        else:
            self.angle += diff * self.animation_speed

        self.darea.queue_draw()
        return True

    def on_draw(self, widget, cr):
        cr.set_line_width(2)
        cr.set_source_rgb(0, 0, 0)

        cx, cy = self.size / 2, self.size / 2
        length = self.size / 3

        cr.translate(cx, cy)
        cr.rotate(self.angle)
        cr.translate(-cx, -cy)

        cr.move_to(cx - length, cy - length / 2)
        cr.line_to(cx, cy + length / 2)
        cr.line_to(cx + length, cy - length / 2)
        cr.stroke()

        return False


# тест окна
win = Gtk.Window(title="ArrowButton Demo")
win.connect("destroy", Gtk.main_quit)

box = Gtk.Box(spacing=10)
win.add(box)

arrow_btn = ArrowButton(48)
box.pack_start(arrow_btn, False, False, 0)

win.show_all()
Gtk.main()
