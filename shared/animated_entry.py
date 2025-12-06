import gi
from typing import Literal
from collections.abc import Iterable
from fabric.widgets.widget import Widget

gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, GLib, Pango, Gdk
import time, math

FRAME_MS = 16


def _hex_to_rgba(hex_str: str):
    s = hex_str.lstrip("#")
    if len(s) == 6:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
        a = 1.0
    elif len(s) == 8:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
        a = int(s[6:8], 16) / 255.0
    else:
        r, g, b, a = 1.0, 1.0, 1.0, 1.0
    rgba = Gdk.RGBA()
    rgba.red = r
    rgba.green = g
    rgba.blue = b
    rgba.alpha = a
    return rgba


class Entry(Gtk.Entry, Widget):
    def __init__(
        self,
        text: str | None = None,
        placeholder: str | None = None,
        editable: bool = True,
        password: bool = False,
        max_length: int = 0,
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
        Gtk.Entry.__init__(self)
        Widget.__init__(
            self,
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
        if text is not None:
            self.set_text(text)
        if placeholder is not None:
            self.set_placeholder_text(placeholder)
        self.set_max_length(max_length)
        self.set_editable(editable)
        self.set_visibility(not password)
        self._blink_period = 0.9
        self._move_tau = 0.06
        self._blink_tau = 0.06
        self._target_x = None
        self._anim_x = None
        self._blink_target = 1.0
        self._blink_alpha = 1.0
        self._last_time = time.monotonic()
        self._timer_id = None
        self._caret_boldness = 0.0
        self._caret_rgba = _hex_to_rgba("#FFFFFF")
        self.connect_after("draw", self._on_draw_after)
        self.connect("notify::cursor-position", lambda *a: self._update_target_x())
        self.connect("changed", lambda *a: self._update_target_x())
        self.connect("size-allocate", lambda *a: self._update_target_x())
        self.connect("realize", lambda *a: self._start_timer())
        self.connect("unrealize", lambda *a: self._stop_timer())
        GLib.idle_add(self._update_target_x)

    @staticmethod
    def _alpha_from_tau(dt: float, tau: float) -> float:
        if tau <= 0:
            return 1.0
        try:
            return 1.0 - math.exp(-dt / tau)
        except Exception:
            return 1.0

    def set_caret_color_hex(self, hex_str: str):
        self._caret_rgba = _hex_to_rgba(hex_str)
        try:
            self.queue_draw()
        except Exception:
            pass

    def set_caret_boldness(self, bold: float):
        try:
            self._caret_boldness = float(bold)
        except Exception:
            self._caret_boldness = 0.0

    def _update_target_x(self):
        layout = self.get_layout()
        if layout is None:
            return False
        try:
            idx = int(self.get_property("cursor-position"))
        except Exception:
            idx = 0
        try:
            layout_index = self.text_index_to_layout_index(idx)
        except Exception:
            layout_index = idx
        try:
            strong, weak = layout.get_cursor_pos(layout_index)
            pango_x = (
                strong.x if strong is not None else (weak.x if weak is not None else 0)
            )
        except Exception:
            try:
                rect = layout.index_to_pos(layout_index)
                pango_x = rect.x
            except Exception:
                pango_x = 0
        px_x = pango_x / Pango.SCALE
        try:
            off_x, off_y = self.get_layout_offsets()
        except Exception:
            off_x, off_y = (0, 0)
        target = off_x + px_x
        if self._anim_x is None:
            self._anim_x = float(target)
        self._target_x = float(target)
        return False

    def _start_timer(self):
        if self._timer_id is None:
            self._last_time = time.monotonic()
            self._timer_id = GLib.timeout_add(FRAME_MS, self._on_frame)

    def _stop_timer(self):
        if self._timer_id is not None:
            try:
                GLib.source_remove(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

    def _on_frame(self):
        now = time.monotonic()
        dt = (
            now - self._last_time
            if self._last_time is not None
            else (FRAME_MS / 1000.0)
        )
        self._last_time = now
        if self._target_x is None:
            self._update_target_x()
        if self._target_x is not None and self._anim_x is not None:
            alpha = self._alpha_from_tau(dt, self._move_tau)
            self._anim_x += (self._target_x - self._anim_x) * alpha
        phase = (now % self._blink_period) / self._blink_period
        sinval = 0.5 + 0.5 * math.sin(2.0 * math.pi * phase - math.pi / 2.0)
        sinval = max(0.02, min(1.0, sinval))
        self._blink_target = sinval
        blink_alpha = self._alpha_from_tau(dt, self._blink_tau)
        self._blink_alpha += (self._blink_target - self._blink_alpha) * blink_alpha
        try:
            self.queue_draw()
        except Exception:
            pass
        return True

    def _on_draw_after(self, widget, cr):
        if not (self.is_focus() and self.get_editable()):
            return False
        layout = self.get_layout()
        if layout is None:
            return False
        if self._target_x is None:
            self._update_target_x()
        if self._anim_x is None:
            return False
        x = float(self._anim_x)
        try:
            ink_rect, logical_rect = layout.get_extents()
            caret_height = logical_rect.height / Pango.SCALE
            layout_off_x, layout_off_y = self.get_layout_offsets()
            caret_y = layout_off_y + (logical_rect.y / Pango.SCALE)
        except Exception:
            alloc = self.get_allocation()
            caret_height = alloc.height * 0.66
            layout_off_x, layout_off_y = self.get_layout_offsets()
            caret_y = layout_off_y + (alloc.height - caret_height) / 2.0
        alloc = self.get_allocation()
        if x < 0 or x > alloc.width:
            return False
        base_width = 1.0
        caret_width = max(1.0, base_width + float(self._caret_boldness))
        cr.set_source_rgba(
            self._caret_rgba.red,
            self._caret_rgba.green,
            self._caret_rgba.blue,
            float(self._blink_alpha) * self._caret_rgba.alpha,
        )
        cr.rectangle(x - (caret_width / 2.0), caret_y, caret_width, caret_height)
        cr.fill()
        return False
