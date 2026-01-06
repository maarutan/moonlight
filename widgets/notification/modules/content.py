import re
from typing import TYPE_CHECKING

from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from shared.app_icon import AppIcon

from utils.widget_utils import setup_cursor_hover

if TYPE_CHECKING:
    from .core import NotifyCore


class ContentBox(Box):
    def __init__(
        self,
        notify_core: "NotifyCore",
    ):
        self.notify_core = notify_core
        self.notif = self.notify_core._notification
        super().__init__(
            name="notification-content",
            spacing=4,
            orientation="v",
            h_expand=True,
            v_expand=True,
        )

        label_summary = Label(
            label=self.notif.summary,
            ellipsization="middle",
        )
        title_bottom_Box = Box(
            name="notification-content-title-bottom",
            orientation="h",
            h_expand=True,
            v_expand=True,
        )

        title_bottom_Box.add(label_summary)

        label_body = Label(
            name="notification-content-body",
            v_align="start",
            h_align="start",
            wrap=True,
            x_align=0.0,
            style_classes="body",
        )

        self.add(title_bottom_Box)

        if not len(self.notif.body) == 0:
            label_body.set_text(self.wrap_long_words(self.notif.body))
            self.add(label_body)

    def wrap_long_words(self, text: str) -> str:
        max_len = self.notify_core.notify_widget.confh.config["max-chars-width"]
        result = []

        tokens = re.split(r"(\s+|/)", text)

        current = ""
        for tok in tokens:
            if len(current) + len(tok) <= max_len:
                current += tok
            else:
                if current:
                    result.append(current)
                current = tok

            while len(current) > max_len:
                result.append(current[: max_len - 1] + "-")
                current = current[max_len - 1 :]

        if current:
            result.append(current)

        return "\n".join(result)
