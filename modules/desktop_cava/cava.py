import configparser
import ctypes
import os
import signal
import struct
import subprocess
import tempfile
from math import pi

from fabric.widgets.overlay import Overlay
from gi.repository import Gdk, GLib, Gtk  # type: ignore
from loguru import logger
from config import CAVA_DESKTOP


def get_bars(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return int(config["general"]["bars"])


bars = get_bars(CAVA_DESKTOP)


def set_death_signal():
    """Ensure cava dies with the parent process."""
    libc = ctypes.CDLL("libc.so.6")
    PR_SET_PDEATHSIG = 1
    libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)


class Cava:
    NONE = 0
    RUNNING = 1
    RESTARTING = 2
    CLOSING = 3

    def __init__(self, mainapp):
        self.bars = bars
        self.path = tempfile.mktemp(prefix="cava_", dir="/tmp")
        self.cava_config_file = self._patch_config(CAVA_DESKTOP)

        self.data_handler = mainapp.draw.update
        self.command = ["cava", "-p", self.cava_config_file]
        self.state = self.NONE

        self.env = dict(os.environ)
        self.env["LC_ALL"] = "en_US.UTF-8"

        # format: 16-bit little-endian
        self.byte_type, self.byte_size, self.byte_norm = ("H", 2, 65535)

        if not os.path.exists(self.path):
            os.mkfifo(self.path)

        self.fifo_fd = None
        self.channel = None
        self.io_watch_id = None
        self.process = None

    def _patch_config(self, original_cfg: str) -> str:
        """Создать временный конфиг с raw_target = self.path"""
        config = configparser.ConfigParser()
        config.read(original_cfg)

        if "output" not in config:
            config["output"] = {}
        config["output"]["method"] = "raw"
        config["output"]["raw_target"] = self.path
        config["output"]["data_format"] = "binary"
        config["output"]["bits"] = "16"
        config["output"]["channels"] = "mono"

        tmp_cfg = tempfile.mktemp(prefix="cava_cfg_", dir="/tmp")
        with open(tmp_cfg, "w") as f:
            config.write(f)

        return tmp_cfg

    def _run_process(self):
        logger.debug("Launching cava process...")
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=self.env,
                preexec_fn=set_death_signal,
            )
            logger.debug("cava successfully launched!")
            self.state = self.RUNNING
        except Exception:
            logger.exception("Fail to launch cava")

    def _start_io_reader(self):
        logger.debug("Activating GLib IOChannel for cava stream handler")
        self.fifo_fd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
        # обертка вокруг FD
        self.channel = GLib.IOChannel.unix_new(self.fifo_fd)
        self.channel.set_encoding(None)  # raw-байты
        self.channel.set_buffered(False)

        # регистрируем callback
        self.io_watch_id = GLib.io_add_watch(
            self.channel, GLib.IO_IN, self._io_callback
        )

    def _io_callback(self, source, condition):
        chunk = self.byte_size * self.bars
        try:
            data = os.read(self.fifo_fd, chunk)
        except OSError:
            return True

        if len(data) < chunk:
            return True

        fmt = "<" + (self.byte_type * self.bars)
        sample = [i / self.byte_norm for i in struct.unpack(fmt, data)]
        GLib.idle_add(self.data_handler, sample)
        return True

    def start(self):
        self._start_io_reader()
        self._run_process()

    def restart(self):
        if self.state == self.RUNNING:
            logger.debug("Restarting cava process...")
            self.state = self.RESTARTING
            if self.process and self.process.poll() is None:
                self.process.kill()
        elif self.state == self.NONE:
            logger.warning("Restarting cava process after crash...")
            self.start()

    def close(self):
        self.state = self.CLOSING
        if self.process and self.process.poll() is None:
            self.process.kill()
        if self.io_watch_id:
            GLib.source_remove(self.io_watch_id)
        if self.channel:
            self.channel.shutdown(True)
            self.channel = None
        if self.fifo_fd:
            os.close(self.fifo_fd)
            self.fifo_fd = None
        for p in (self.path, self.cava_config_file):
            if p and os.path.exists(p):
                os.remove(p)


class AttributeDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, 3)

    def __setattr__(self, attr, value):
        self[attr] = value


class Spectrum:
    def __init__(self):
        self.silence_value = 0
        self.audio_sample = []
        self.color = None

        self.area = Gtk.DrawingArea()
        self.area.connect("draw", self.redraw)
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self.sizes = AttributeDict()
        self.sizes.area = AttributeDict()
        self.sizes.bar = AttributeDict()

        self.silence = 10
        self.max_height = 12

        self.area.connect("configure-event", self.size_update)
        self.color_update()

    def is_silence(self, value):
        self.silence_value = 0 if value > 0 else self.silence_value + 1
        return self.silence_value > self.silence

    def update(self, data):
        self.color_update()
        self.audio_sample = data
        if not self.is_silence(self.audio_sample[0]):
            self.area.queue_draw()
        elif self.silence_value == (self.silence + 1):
            self.audio_sample = [0] * self.sizes.number
            self.area.queue_draw()

    def redraw(self, widget, cr):
        dx = self.sizes.padding
        shadow_offset = 3  # смещение тени

        for value in self.audio_sample:
            bar_width = self.sizes.area.width / self.sizes.number - self.sizes.padding
            radius = bar_width / 2
            bar_height = max(self.sizes.bar.height * min(value, 1), self.sizes.zero) / 2
            bar_height = min(bar_height, self.max_height)

            # ---- ТЕНЬ ----
            cr.set_source_rgba(0, 0, 0, 0.4)  # чёрная тень с прозрачностью
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

            # ---- ОСНОВНОЙ БАР ----
            cr.set_source_rgba(*self.color)
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
        self.sizes.number = bars
        self.sizes.padding = 100 / bars
        self.sizes.zero = 0

        self.sizes.area.width = self.area.get_allocated_width()
        self.sizes.area.height = self.area.get_allocated_height() - 2

        tw = self.sizes.area.width - self.sizes.padding * (self.sizes.number - 1)
        self.sizes.bar.width = max(int(tw / self.sizes.number), 1)
        self.sizes.bar.height = self.sizes.area.height

    def color_update(self):
        color = "#ffffff"
        red = int(color[1:3], 16) / 255
        green = int(color[3:5], 16) / 255
        blue = int(color[5:7], 16) / 255
        self.color = Gdk.RGBA(red=red, green=green, blue=blue, alpha=1.0)


class SpectrumRender:
    def __init__(self, is_horizontal, mode=None, **kwargs):
        super().__init__(**kwargs)
        self.is_horizontal = is_horizontal
        self.draw = Spectrum()
        self.cava = Cava(self)
        self.cava.start()

    def get_spectrum_box(self):
        box = Overlay(name="cavalcade-desktop", h_align="center", v_align="center")
        box.set_size_request(980, 100)
        box.add_overlay(self.draw.area)
        box.show_all()
        return box
