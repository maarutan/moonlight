import math
from fabric.widgets.eventbox import EventBox  # type: ignore
from fabric.utils.helpers import Gtk, GLib, cairo  # type: ignore
from utils.hex_to_rgb import hex_to_rgb
from utils.colors_parse import colors


class ArrowIcon(Gtk.DrawingArea):
    def __init__(
        self, size: int = 12, angle_deg: float = 0.0, anim_duration_ms: int = 150
    ):
        super().__init__()

        self._size = size
        self._angle = angle_deg
        self._target_angle = angle_deg
        self._start_angle = angle_deg
        self._anim_running = False
        self._anim_start_time = 0
        self._anim_duration = anim_duration_ms
        self.set_size_request(size, size)

        ctx = self.get_style_context()
        ctx.add_class("arrow-icon")

        self.connect("draw", self._on_draw)

    def set_angle(self, angle_deg: float):
        self._angle = angle_deg
        self._target_angle = angle_deg
        self._anim_running = False
        self.queue_draw()

    def animate_to(self, angle_deg: float):
        if math.isclose(angle_deg, self._angle, abs_tol=0.1):
            self.set_angle(angle_deg)
            return

        self._start_angle = self._angle
        self._target_angle = angle_deg
        self._anim_start_time = GLib.get_monotonic_time()
        if not self._anim_running:
            self._anim_running = True
            GLib.timeout_add(16, self._tick)

    def _tick(self) -> bool:
        if not self._anim_running:
            return False

        now_us = GLib.get_monotonic_time()
        elapsed_ms = (now_us - self._anim_start_time) / 1000.0
        t = elapsed_ms / float(self._anim_duration)

        if t >= 1.0:
            t = 1.0
            self._anim_running = False

        new_angle = self._start_angle + (self._target_angle - self._start_angle) * t
        self._angle = new_angle
        self.queue_draw()

        return self._anim_running

    def _on_draw(self, widget: Gtk.DrawingArea, cr: cairo.Context):
        alloc = self.get_allocation()
        w = alloc.width
        h = alloc.height

        cr.save()

        cx = w / 2.0
        cy = h / 2.0
        cr.translate(cx, cy)

        angle_rad = math.radians(self._angle)
        cr.rotate(angle_rad)

        size = min(w, h) * 0.4
        p1 = (size, 0)
        p2 = (-size, -size)
        p3 = (-size, size)

        cr.move_to(*p1)
        cr.line_to(*p2)
        cr.line_to(*p3)
        cr.close_path()

        style_ctx = self.get_style_context()
        fg_rgba = style_ctx.get_color(Gtk.StateFlags.NORMAL)  # type: ignore
        cr.set_source_rgba(fg_rgba.red, fg_rgba.green, fg_rgba.blue, fg_rgba.alpha)

        cr.fill()
        cr.restore()

        return False


class ArrowIconTwo(EventBox):
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

        GLib.timeout_add(16, self.animate)  # ~60 FPS

    def on_click(self, *_):
        self.target_angle = math.pi if self.target_angle == 0 else 0

    def open(self):
        self.target_angle = math.pi

    def close(self):
        self.target_angle = 0

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
        cr.set_source_rgb(*hex_to_rgb(colors["text"]))

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
