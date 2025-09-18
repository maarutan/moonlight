import os
from pathlib import Path
import struct
import subprocess
import tempfile
import configparser

from gi.repository import GLib  # type: ignore
from loguru import logger

from ..utils import set_death_signal
from ._config_handler import ConfigHandlerCavalade


class Cava:
    NONE = 0
    RUNNING = 1
    RESTARTING = 2
    CLOSING = 3

    def __init__(
        self,
        mainapp,
        name: str,
        config_file: str | Path,
        config_dir: str | Path,
    ):
        # путь к FIFO
        self.path = tempfile.mktemp(
            dir="/tmp",
            prefix="cava_",
        )

        # обработка конфига
        self.cfg_dir = config_dir
        self.confh = ConfigHandlerCavalade(
            name=name,
            file=config_file,
            dir=self.cfg_dir,
        )
        self.bars = self.confh.cava.general()["bars"]
        # пропатченный конфиг для запуска
        self.cfg_handled_file = self._patch_config(self.confh.config_file.as_posix())

        # обработчик данных (назначается извне, см. SpectrumRender)
        self.data_handler = getattr(mainapp, "draw", None)
        if self.data_handler:
            self.data_handler = self.data_handler.update

        # команда запуска cava
        self.command = ["cava", "-p", self.cfg_handled_file]
        self.state = self.NONE

        self.env = dict(os.environ)
        self.env["LC_ALL"] = "en_US.UTF-8"

        # формат: 16-bit little-endian
        self.byte_type, self.byte_size, self.byte_norm = ("H", 2, 65535)

        if not os.path.exists(self.path):
            os.mkfifo(self.path)

        self.fifo_fd = None
        self.fifo_dummy_fd = None
        self.channel = None
        self.io_watch_id = None
        self.process = None

    def _patch_config(self, original_cfg: str) -> str:
        """Создать временный ini с нужным output (raw -> fifo)."""
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
        logger.debug(f"Launching cava process with config {self.cfg_handled_file}")
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
        # reader
        self.fifo_fd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
        # dummy writer — без него сразу EOF
        self.fifo_dummy_fd = os.open(self.path, os.O_WRONLY | os.O_NONBLOCK)

        self.channel = GLib.IOChannel.unix_new(self.fifo_fd)
        self.channel.set_encoding(None)  # raw-байты
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
        sample = [i / self.byte_norm for i in struct.unpack(fmt, data)]
        if self.data_handler:
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
        if self.fifo_dummy_fd:
            os.close(self.fifo_dummy_fd)
            self.fifo_dummy_fd = None
        for p in (self.path, self.cfg_handled_file):
            if p and os.path.exists(p):
                os.remove(p)
