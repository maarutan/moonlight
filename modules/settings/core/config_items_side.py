from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from utils.constants import Const
from typing import TYPE_CHECKING

from .modules.user_dashboard import UserDashboardConfig
from .modules.application_settings.settings import ApplicationConfig

if TYPE_CHECKING:
    from ..start_menu import StartMenu


class ItemsSideConfig(Box):
    def __init__(self, init_class: "StartMenu") -> None:
        self.cfg = init_class
        super().__init__(
            name="sm_items-side-config-box",
            orientation="v",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
        )
        self.config = [
            {
                "item_name": "user-dashboard",
                "widget": UserDashboardConfig(self.cfg),
            },
            {
                "item_name": "application-config",
                "widget": ApplicationConfig(self.cfg),
            },
        ]

        self.placeholder_picture = Image(
            image_file=Const.PLACEHOLDER_IMAGE_GHOST.as_posix(),
            size=400,
            h_align="fill",
            v_align="fill",
        )
        self.scroll = ScrolledWindow(
            name="sm_scroll-window",
            h_scroll=False,
            v_scroll=True,
            h_align="fill",
            v_align="fill",
            v_scrollbar_policy="always",
            h_scrollbar_policy="never",
            min_content_size=(600, 600),
        )
        self.wrapper = Box(
            orientation="v",
            h_align="fill",
            v_align="fill",
        )
        self.content_box = Box(
            orientation="v",
            h_align="fill",
            v_align="fill",
        )
        if self.cfg.current_select is None:
            self.content_box.add(self.placeholder_picture)
        self.wrapper.add(self.content_box)
        self.scroll.add(self.wrapper)

        self.add(self.scroll)

    def update_preview(self, name: str):
        for child in list(self.content_box.get_children()):
            self.content_box.remove(child)
        for module in self.config:
            if module["item_name"] == name:
                self.content_box.add(module["widget"])
                break
        else:
            self.content_box.add(self.placeholder_picture)
