from typing import TYPE_CHECKING

from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from shared.app_icon import AppIcon

from utils.widget_utils import setup_cursor_hover

if TYPE_CHECKING:
    from .core import NotifyCore


class NotifyTitle(Box):
    def __init__(
        self,
        class_init: "NotifyCore",
    ):
        self.conf = class_init
        self.notif = self.conf._notification
        super().__init__(
            name="notification-title",
            spacing=4,
            orientation="h",
            h_expand=True,
            v_expand=True,
        )

        title_box = Box(
            orientation="h",
            h_expand=True,
            v_expand=True,
        )

        if icon := self.notif.app_icon == "" or self.notif.app_icon is None:
            icon = self.notif.app_name
        else:
            icon = self.notif.app_icon

        icon_app = AppIcon(icon, icon_size=self.conf.conf.config["title-icon-size"])
        title_box.pack_start(
            icon_app,
            False,
            False,
            0,
        )
        title_box.add(Label(f" {self.notif.app_name} "))
        btn = Button(
            name="notification_close-button",
            label="x",
            v_align="center",
            h_align="end",
            on_clicked=lambda *_: self.notif.close(),
        )
        setup_cursor_hover(btn)
        title_box.pack_end(
            btn,
            False,
            False,
            0,
        )
        self.add(title_box)
