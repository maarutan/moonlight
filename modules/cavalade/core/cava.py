import os
from pathlib import Path
import struct
import subprocess
import tempfile
import configparser
import fcntl

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

        # Ensure pid file exists (and parent dir)
        Path(Const.CAVA_PIDS).parent.mkdir(parents=True, exist_ok=True)
        Path(Const.CAVA_PIDS).touch(exist_ok=True)

        if not os.path.exists(self.path):
            os.mkfifo(self.path)

        self.fifo_fd = None
        self.fifo_dummy_fd = None
        self.channel = None
        self.io_watch_id = None
        self.process = None
        self.child_watch_id = None  # GLib child watch source id
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

    # ---------- PID file helpers ----------

    def _append_pid_file(self, pid: int) -> None:
        """Append pid as a new line (atomic-ish with flock)."""
        try:
            p = Path(Const.CAVA_PIDS)
            p.parent.mkdir(parents=True, exist_ok=True)
            # Open for append (create if not exists)
            with p.open("a+", encoding="utf-8") as f:
                # use advisory lock to avoid races
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                except Exception:
                    pass
                f.write(f"{int(pid)}\n")
                f.flush()
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
            logger.debug(f"Appended cava pid {pid} to {p}")
        except Exception:
            logger.exception("Failed to append cava pid to file")

    def _remove_pid_from_file(self, pid: int) -> None:
        """Remove all lines equal to pid (keeps other pids)."""
        try:
            p = Path(Const.CAVA_PIDS)
            if not p.exists():
                return
            # read with lock
            try:
                with p.open("r+", encoding="utf-8") as f:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    except Exception:
                        pass
                    lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                    new_lines = [ln for ln in lines if int(ln) != int(pid)]
                    f.seek(0)
                    f.truncate(0)
                    if new_lines:
                        f.write("\n".join(new_lines) + "\n")
                    # unlock automatically on close
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass
            except FileNotFoundError:
                return
            logger.debug(f"Removed cava pid {pid} from {p}")
        except Exception:
            logger.exception("Failed to remove cava pid from file")

    # child-watch callback: removes pid when cava terminates/crashes
    def _on_child_exit(self, pid, status):
        logger.debug(f"cava child {pid} exited (status {status})")
        try:
            self._remove_pid_from_file(pid)
        except Exception:
            logger.exception("Error while removing pid on child exit")
        # clear process reference if it matches
        if self.process and self.process.pid == pid:
            self.process = None
        self.state = self.NONE
        # return False to remove the source automatically
        return False

    # ---------- process control ----------
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

            # write pid to file
            if self.process and self.process.pid:
                self._append_pid_file(self.process.pid)

                # register a GLib child watch so we know when it exits and can clean up
                try:
                    # GLib.child_watch_add returns a source id; store it so we can remove if needed
                    self.child_watch_id = GLib.child_watch_add(
                        self.process.pid, self._on_child_exit, None
                    )
                except Exception:
                    # On some platforms the signature may differ; still we catch exceptions
                    logger.exception("Failed to register GLib.child_watch_add")
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
                try:
                    pid = self.process.pid
                    self.process.kill()
                except Exception:
                    logger.exception("Failed to kill cava on restart")
                finally:
                    # remove pid entry immediately
                    try:
                        if pid:
                            self._remove_pid_from_file(pid)
                    except Exception:
                        logger.exception("Failed removing pid after restart")
        elif self.state == self.NONE:
            logger.warning("Restarting cava process after crash...")
            self.start()

    def close(self):
        self.state = self.CLOSING
        # kill process if running
        if self.process and self.process.poll() is None:
            try:
                pid = self.process.pid
                self.process.kill()
            except Exception:
                logger.exception("Failed to kill cava on close")
            finally:
                try:
                    if pid:
                        self._remove_pid_from_file(pid)
                except Exception:
                    logger.exception("Failed removing pid on close")

        # remove child watch if present
        if getattr(self, "child_watch_id", None):
            try:
                GLib.source_remove(self.child_watch_id)  # type: ignore
            except Exception:
                logger.exception("Failed to remove child watch")
            self.child_watch_id = None

        if self.io_watch_id:
            try:
                GLib.source_remove(self.io_watch_id)
            except Exception:
                logger.exception("Failed to remove io watch")
            self.io_watch_id = None

        if self.channel:
            try:
                self.channel.shutdown(True)
            except Exception:
                logger.exception("Failed to shutdown channel")
            self.channel = None

        if self.fifo_fd:
            try:
                os.close(self.fifo_fd)
            except Exception:
                logger.exception("Failed to close fifo_fd")
            self.fifo_fd = None

        if self.fifo_dummy_fd:
            try:
                os.close(self.fifo_dummy_fd)
            except Exception:
                logger.exception("Failed to close fifo_dummy_fd")
            self.fifo_dummy_fd = None
