from math import pi
from gi.repository import Gdk, Gtk, GLib  # type: ignore
from ..utils import AttributeDict
from utils.colors_parse import colors
from utils.hex_to_rgb import hex_to_rgb


class Spectrum:
    def __init__(self, bars: int, fps: int = 30):
        self.silence_value = 0
        self.audio_sample: list[float] = []
        self.color = Gdk.RGBA(red=1.0, green=1.0, blue=1.0, alpha=1.0)

        self.bars = bars
        self.area = Gtk.DrawingArea()
        self.area.connect("draw", self.redraw)
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)  # type: ignore

        self.sizes = AttributeDict()
        self.sizes.area = AttributeDict()
        self.sizes.bar = AttributeDict()

        self.silence = 10
        self.max_height = 12

        self.area.connect("configure-event", self.size_update)

        interval = int(1000 / fps)
        GLib.timeout_add(interval, self._throttled_draw)

    def is_silence(self, value):
        self.silence_value = 0 if value > 0 else self.silence_value + 1
        return self.silence_value > self.silence

    def update(self, data: list[float]):
        self.audio_sample = data

    def _throttled_draw(self):
        if self.audio_sample:
            if not self.is_silence(self.audio_sample[0]):
                self.area.queue_draw()
            elif self.silence_value == (self.silence + 1):
                self.audio_sample = [0] * self.sizes.number
                self.area.queue_draw()
        return True

    def redraw(self, widget, cr):
        dx = self.sizes.padding
        shadow_offset = 3

        for value in self.audio_sample:
            bar_width = self.sizes.area.width / self.sizes.number - self.sizes.padding
            radius = bar_width / 2
            bar_height = max(self.sizes.bar.height * min(value, 1), self.sizes.zero) / 2
            bar_height = min(bar_height, self.max_height)

            cr.set_source_rgba(0, 0, 0, 0.4)
            cr.rectangle(
                dx + shadow_offset,
                (self.sizes.area.height / 2) - bar_height + shadow_offset,
                bar_width,
                bar_height * 2,
            )
            cr.arc(
                dx + radius + shadow_offset,
                (self.sizes.area.height / 2) - bar_height + shadow_offset,
                radius,
                0,
                2 * pi,
            )
            cr.arc(
                dx + radius + shadow_offset,
                (self.sizes.area.height / 2) + bar_height + shadow_offset,
                radius,
                0,
                2 * pi,
            )
            cr.close_path()
            cr.fill()

            r, g, b = hex_to_rgb(colors["text"])
            cr.set_source_rgb(r, g, b)
            cr.rectangle(
                dx,
                (self.sizes.area.height / 2) - bar_height,
                bar_width,
                bar_height * 2,
            )
            cr.arc(
                dx + radius,
                (self.sizes.area.height / 2) - bar_height,
                radius,
                0,
                2 * pi,
            )
            cr.arc(
                dx + radius,
                (self.sizes.area.height / 2) + bar_height,
                radius,
                0,
                2 * pi,
            )
            cr.close_path()
            cr.fill()

            dx += bar_width + self.sizes.padding

    def size_update(self, *args):
        self.sizes.number = self.bars
        self.sizes.padding = 100 / self.bars
        self.sizes.zero = 0

        self.sizes.area.width = self.area.get_allocated_width()
        self.sizes.area.height = self.area.get_allocated_height() - 2

        tw = self.sizes.area.width - self.sizes.padding * (self.sizes.number - 1)
        self.sizes.bar.width = max(int(tw / self.sizes.number), 1)
        self.sizes.bar.height = self.sizes.area.height
