from typing import TYPE_CHECKING
from fabric.notifications import Notifications
from fabric.widgets.box import Box
from .modules.core import NotifyCore

if TYPE_CHECKING:
    from .notify_widget import NotificationWidget


class NotificationService:
    """Add notifications to a wrapper Box"""

    def __init__(
        self,
        notify_widget: "NotificationWidget",
        add_to: Box,
    ):
        self.notify_widget = notify_widget
        self._add_to = add_to
        self._active_widgets: dict[int, NotifyCore] = {}

        self._service = Notifications(on_notification_added=self._on_added)

    def _on_added(self, service: Notifications, nid: int):
        notif = service.get_notification_from_id(nid)
        if notif is None:
            return

        widget = NotifyCore(
            notify_widget=self.notify_widget,
            notification=notif,
            active_widgets=self._active_widgets,
            server=self._service,
        )

        self._add_to.add(widget)
