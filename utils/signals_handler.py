import signal
from utils.constants import Const
from utils.jsonc import jsonc
from fabric.utils import GLib


class SignalsHandler:
    def __init__(self):
        self.path = Const.SIGNAL_DATABASE

    def write_signal(
        self,
        signal_name: str,
        pid: int,
    ): 
