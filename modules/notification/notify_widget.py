from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow
from .notifications import NotificationService
from .config import NotificationConfig

widget_name = "notification"
conf = NotificationConfig(widget_name)
enabled = conf.get_option(f"{widget_name}.enabled", True)

if not enabled:
    NotificationWidget = None  # type: ignore
else:

    class NotificationWidget(WaylandWindow):
        def __init__(self):
            self.confh = conf
            self.widget_name = widget_name
            self.config = self.confh.get_option(self.widget_name)

            super().__init__(
                name="notification-popup",
                margin=self.config["margin"],
                anchor=self.config["anchor"],
                layer=self.config["layer"],
                v_expand=True,
                h_expand=True,
                visible=True,
                all_visible=True,
            )

            self.main_box = Box(
                size=2,  # so it's not ignored by the compositor
                spacing=4,
                orientation="v",
                v_expand=True,
                h_expand=True,
            )
            NotificationService(
                init_class=self,
                add_to=self.main_box,
            )
            self.add(self.main_box)
