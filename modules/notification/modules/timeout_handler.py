from typing import TYPE_CHECKING
from fabric.utils.helpers import invoke_repeater

if TYPE_CHECKING:
    from .core import NotifyCore


class TimeOutHandler:
    def __init__(self, class_init: "NotifyCore"):
        self.conf = class_init
        self.notif = self.conf._notification

        timeout = self.notif.timeout
        if timeout <= 0:
            timeout = self.conf.conf.config["default-timeout"]

        invoke_repeater(
            timeout,
            lambda *_: self.notif.close("expired"),
            initial_call=False,
        )
