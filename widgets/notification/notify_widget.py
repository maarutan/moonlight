from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow
from .notifications import NotificationService
from .config import ConfigHandlerNotification

config_handler = ConfigHandlerNotification()

if not config_handler.config["enabled"]:
    NotificationWidget = None  # type: ignore
else:

    class NotificationWidget(WaylandWindow):
        def __init__(self):
            self.confh = config_handler

            self.main_box = Box(
                size=2,  # so it's not ignored by the compositor
                spacing=4,
                orientation="v",
                v_expand=True,
                h_expand=True,
            )
            NotificationService(
                notify_widget=self,
                add_to=self.main_box,
            )

            super().__init__(
                name="notification-popup",
                margin=self.confh.config["margin"],
                anchor=self.confh.config["anchor"],
                layer=self.confh.config["layer"],
                v_expand=True,
                h_expand=True,
                visible=True,
                all_visible=True,
                child=self.main_box,
            )
