from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from shared.linearprogressbar import LinearProgressBar

if TYPE_CHECKING:
    from .core import NotifyCore


class ProgressBar(Box):
    def __init__(self, class_init: "NotifyCore"):
        self.conf = class_init
        self.notif = self.conf._notification
        self.hint_value = self.notif.do_get_hint_entry("value")

        super().__init__(
            name="notification-progress-bar-box",
        )

        self.progress_bar = LinearProgressBar(
            name="notification-progress-bar",
            h_align="fill",
            h_expand=True,
            line_width=self.conf.conf.config["progress-bar-line-width"],
            min_value=0,
            max_value=100,
            value=0.0,
            size=16,
        )

        if isinstance(self.hint_value, int):
            self.progress_bar.value = float(self.hint_value)

        self.progress_bar.line_style = self.conf.conf.config["progress-bar-line-style"]

        if not self.hint_value is None:
            self.add(self.progress_bar)
