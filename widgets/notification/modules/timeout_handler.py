from typing import TYPE_CHECKING
from fabric.utils.helpers import invoke_repeater

if TYPE_CHECKING:
    from .core import NotifyCore


class TimeOutHandler:
    def __init__(self, notify_core: "NotifyCore"):
        self.notify_core = notify_core
        self.notif = self.notify_core._notification

        timeout = self.notif.timeout
        if timeout <= 0:
            timeout = self.notify_core.notify_widget.confh.config["default-timeout"]

        invoke_repeater(
            timeout,
            lambda *_: self.notif.close("expired"),
            initial_call=False,
        )
