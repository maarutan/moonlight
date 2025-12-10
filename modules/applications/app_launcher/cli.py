import os
import signal
from typing import TYPE_CHECKING

from fabric.utils import GLib, idle_add

from utils.constants import Const

if TYPE_CHECKING:
    from .launcher import AppLauncher


class ALCli:
    def __init__(self, class_init: "AppLauncher"):
        self.conf = class_init

        Const.APP_LAUNCHER_PID.write_text(str(os.getpid()))
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, self._on_usr1)

    def start_app(self):
        self.conf.tools.toggle("show")

    def _on_usr1(self):
        idle_add(self.start_app)
        return True
