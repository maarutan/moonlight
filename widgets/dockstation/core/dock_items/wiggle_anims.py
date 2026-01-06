from fabric.utils import GLib
from random import uniform
import math


class Wiggle:
    def __init__(self, button, confh):
        self.button = button
        self.confh = confh
        cfg_amp = float(self.confh.config.get("wiggle-amplitude", 12))
        cfg_freq = float(self.confh.config.get("wiggle-frequency", 6.0))
        self._margins = {"top": 0.0, "bottom": 0.0, "start": 0.0, "end": 0.0}
        self._angle = uniform(0.0, 2 * math.pi)
        self._dir_x = math.cos(self._angle)
        self._dir_y = math.sin(self._angle)
        base_phase = uniform(0, math.pi * 2)
        self._x_phase = base_phase + uniform(0.0, 1.5)
        self._y_phase = base_phase + uniform(1.5, 3.0)
        self._amp = max(2.0, cfg_amp * (0.7 + uniform(-0.2, 0.4)))
        self._freq = max(2.0, cfg_freq * (0.8 + uniform(-0.2, 0.6)))
        self._interp = 0.14
        self._fade_interp = 0.18
        self.tick_id = None
        self.fade_id = None
        self.is_wiggling = False

    def _tick(self):
        t = GLib.get_monotonic_time() / 1_000_000.0
        sin_x = math.sin(2 * math.pi * self._freq * t + self._x_phase)
        sin_y = math.sin(2 * math.pi * self._freq * t + self._y_phase)
        offset_x = self._dir_x * sin_x * self._amp
        offset_y = self._dir_y * sin_y * self._amp
        start_target = max(0.0, offset_x)
        end_target = max(0.0, -offset_x)
        top_target = max(0.0, offset_y)
        bottom_target = max(0.0, -offset_y)
        targets = {
            "start": start_target,
            "end": end_target,
            "top": top_target,
            "bottom": bottom_target,
        }
        for k in self._margins:
            self._margins[k] += (targets[k] - self._margins[k]) * self._interp
        self.button.set_margin_top(int(round(self._margins["top"])))
        self.button.set_margin_bottom(int(round(self._margins["bottom"])))
        self.button.set_margin_start(int(round(self._margins["start"])))
        self.button.set_margin_end(int(round(self._margins["end"])))
        return self.is_wiggling

    def start(self):
        dock = self.button._dockapp
        if dock._selected:
            return
        if self.tick_id:
            return
        if self.fade_id:
            GLib.source_remove(self.fade_id)
            self.fade_id = None
        self.is_wiggling = True
        self.tick_id = GLib.timeout_add(15, self._tick)

    def stop(self):
        self.is_wiggling = False
        if self.tick_id:
            GLib.source_remove(self.tick_id)
            self.tick_id = None
        if self.fade_id:
            GLib.source_remove(self.fade_id)
        self.fade_id = GLib.timeout_add(20, self._fade_to_zero)

    def _fade_to_zero(self):
        done = all(abs(v) < 0.4 for v in self._margins.values())
        if done:
            self.button.set_margin_top(0)
            self.button.set_margin_bottom(0)
            self.button.set_margin_start(0)
            self.button.set_margin_end(0)
            if self.fade_id:
                GLib.source_remove(self.fade_id)
                self.fade_id = None
            return False
        for k in self._margins:
            self._margins[k] += (0.0 - self._margins[k]) * self._fade_interp
        self.button.set_margin_top(int(round(self._margins["top"])))
        self.button.set_margin_bottom(int(round(self._margins["bottom"])))
        self.button.set_margin_start(int(round(self._margins["start"])))
        self.button.set_margin_end(int(round(self._margins["end"])))
        return True
