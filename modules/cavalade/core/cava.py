import os
from pathlib import Path
import struct
import subprocess
import tempfile
import configparser

from gi.repository import GLib  # pyright: ignore
from loguru import logger

from utils.constants import Const

from ..utils import set_death_signal

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cavalade import SpectrumRender


class Cava:
    NONE = 0
    RUNNING = 1
    RESTARTING = 2
    CLOSING = 3

    def __init__(
        self,
        class_init: "SpectrumRender",
        mainapp,
    ):
        self.path = tempfile.mktemp(
            dir="/tmp",
            prefix="cava_",
        )
        self.conf = class_init
        self.confh = self.conf.confh

        config = self.confh.get_widget_config()
        self.bars = config.get("general", {}).get("bars", 50)
        self.config_ini = Const.CAVA_LOCAL_DIR / f"{self.conf.name}.ini"

        self.data_handler = getattr(mainapp, "draw", None)
        if self.data_handler:
            self.data_handler = self.data_handler.update

        self.command = ["cava", "-p", self.config_ini]
        self.state = self.NONE

        self.env = dict(os.environ)
        self.env["LC_ALL"] = "en_US.UTF-8"

        self.byte_type, self.byte_size, self.byte_norm = ("H", 2, 65535)

        if not os.path.exists(self.path):
            os.mkfifo(self.path)

        self.fifo_fd = None
        self.fifo_dummy_fd = None
        self.channel = None
        self.io_watch_id = None
        self.process = None
        self.last_sample = None
        GLib.timeout_add(33, self._emit_sample)

    def _patch_config(self) -> str:
        config = configparser.ConfigParser()
        config.read(self.config_ini)

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
        logger.debug(
            f"Activating GLib IOChannel for cava stream handler on {self.path}"
        )

        self.fifo_fd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)

        self.fifo_dummy_fd = os.open(self.path, os.O_WRONLY | os.O_NONBLOCK)

        self.channel = GLib.IOChannel.unix_new(self.fifo_fd)
        self.channel.set_encoding(None)
        self.channel.set_buffered(False)

        self.io_watch_id = GLib.io_add_watch(
            self.channel, GLib.IO_IN, self._io_callback
        )

    def _io_callback(self, source, condition):
        chunk = self.byte_size * self.bars
        try:
            data = os.read(self.fifo_fd or 0, chunk)
        except OSError:
            return True
        if len(data) < chunk:
            return True

        fmt = "<" + (self.byte_type * self.bars)
        self.last_sample = [i / self.byte_norm for i in struct.unpack(fmt, data)]
        return True

    def _emit_sample(self):
        if self.last_sample and self.data_handler:
            self.data_handler(self.last_sample)
        return True

    def start(self):
        patched = self._patch_config()
        self.command = ["cava", "-p", patched]
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
        if self.fifo_dummy_fd:
            os.close(self.fifo_dummy_fd)
            self.fifo_dummy_fd = None
