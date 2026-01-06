from typing import TYPE_CHECKING

from fabric.utils.helpers import invoke_repeater
from fabric.widgets.box import Box
from fabric.notifications import Notification


from .action_buttons import ActionButtonsHandler
from .timeout_handler import TimeOutHandler
from .images_handler import ImagesHandler
from .replace_handler import ReplaceHandler
from .content import ContentBox
from .progress_bar import ProgressBar
from .title import NotifyTitle


if TYPE_CHECKING:
    from ..notify_widget import NotificationWidget


class NotifyCore(Box):
    def __init__(
        self,
        notify_widget: "NotificationWidget",
        notification: Notification,
        active_widgets: dict[int, "NotifyCore"] = {},
        **kwargs,
    ):
        self.notify_widget = notify_widget
        self._active_widgets = active_widgets
        self._notification = notification
        self._notification.connect("closed", self.on_close)
        ReplaceHandler(self, self._active_widgets)
        TimeOutHandler(self)

        super().__init__(
            size=(self.notify_widget.confh.config["max-width"], -1),
            name="notification-box",
            spacing=2,
            orientation="v",
            v_expand=True,
            h_expand=True,
            **kwargs,
        )
        self.closed_class_name = "notification-closed"
        self.remove_style_class(self.closed_class_name)

        self.add(NotifyTitle(self))
        self.body_container = Box(name="notification-body", spacing=4, orientation="h")
        self.body_container.add(ImagesHandler(self))
        self.body_container.add(ContentBox(self))
        self.add(self.body_container)
        self.add(ActionButtonsHandler(self))
        self.add(ProgressBar(self))

    def on_close(self, *_) -> None:
        self.add_style_class(self.closed_class_name)

        def remove():
            parent.remove(self) if (parent := self.get_parent()) else None  # type: ignore
            self.destroy()

        invoke_repeater(500, remove, initial_call=False)
