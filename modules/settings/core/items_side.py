from pathlib import Path
from typing import TYPE_CHECKING
import os
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.image import Image
from utils.constants import Const
from utils.widget_utils import setup_cursor_hover
from shared.circular_image import CircleImage

if TYPE_CHECKING:
    from ..start_menu import StartMenu


class ItemsSide(Box):
    def __init__(self, init_class: "StartMenu"):
        self.cfg = init_class
        super().__init__(
            name="sm_items-side-box",
            orientation="v",
            h_align="start",
            v_align="center",
            h_expand=True,
            v_expand=True,
        )

        self.scroll = ScrolledWindow(
            name="sm_scroll-window",
            h_scroll=False,
            v_scroll=True,
            h_align="center",
            v_align="center",
            h_expand=True,
            v_expand=True,
            v_scrollbar_policy="always",
            h_scrollbar_policy="never",
            min_content_size=(600, 600),
        )

        self.modules_box = Box(
            orientation="v",
            h_align="center",
            v_align="start",
            h_expand=True,
            v_expand=True,
        )

        username = None
        try:
            username = os.getlogin()
        except OSError:
            username = os.getenv("USER") or "User"

        self.modules = [
            {
                "name": "user-dashboard",
                "image-path": Const.PROFILE_LOGO,
                "title": username,
                "description": f"{Const.APPLICATION_NAME} Account",
                "rounded": True,
                "size": 100,
            },
            {
                "name": "application-config",
                "image-path": Const.APP_ICONS_DIRECTORY / "app.svg",
                "title": Const.APPLICATION_NAME,
                "description": None,
                "rounded": False,
                "size": None,
            },
            {
                "name": "hyprland-config",
                "image-path": Const.APP_ICONS_DIRECTORY / "hyprland.svg",
                "title": "Hyprland",
                "description": None,
                "rounded": False,
                "size": None,
            },
            {
                "name": "wifi-config",
                "image-path": Const.APP_ICONS_DIRECTORY / "wifi.svg",
                "title": "Wifi",
                "description": None,
                "rounded": False,
                "size": None,
            },
            {
                "name": "bluetooth-config",
                "image-path": Const.APP_ICONS_DIRECTORY / "bluetooth.svg",
                "title": "Bluetooth",
                "description": None,
                "rounded": False,
                "size": None,
            },
            {
                "name": "sound-config",
                "image-path": Const.APP_ICONS_DIRECTORY / "sound.svg",
                "title": "Sound",
                "description": None,
                "rounded": False,
                "size": None,
            },
            {
                "name": "date_time-config",
                "image-path": Const.APP_ICONS_DIRECTORY / "date_time.svg",
                "title": "Date & Time",
                "description": None,
                "rounded": False,
                "size": None,
            },
            {
                "name": "battery-config",
                "image-path": Const.APP_ICONS_DIRECTORY / "battery.svg",
                "title": "Battery",
                "description": None,
                "rounded": False,
                "size": None,
            },
            {
                "name": "wallpaper-config",
                "image-path": Const.APP_ICONS_DIRECTORY / "wallpaper.svg",
                "title": "Wallpaper",
                "description": None,
                "rounded": False,
                "size": None,
            },
            {
                "name": "notification",
                "image-path": Const.APP_ICONS_DIRECTORY / "notification.svg",
                "title": "Notification",
                "description": None,
                "rounded": False,
                "size": None,
            },
        ]

        max_len = 0
        for m in self.modules:
            title_len = len(m["title"])
            desc_len = len(m["description"] or "")
            max_len = max(max_len, title_len, desc_len)

        self.buttons: list[Button] = []
        self.button_by_name: dict[str, Button] = {}

        for module in self.modules:
            name = module["name"]
            title = module["title"]
            desc = module["description"] or ""
            title_padded = title.ljust(max_len)
            desc_padded = desc.ljust(max_len)
            label = (
                f"  {title_padded}     \n  {desc_padded}     "
                if desc
                else f"  {title_padded}     "
            )

            image_path = module["image-path"]
            if not image_path.exists() or image_path.stat().st_size == 0:
                image_path = Const.PLACEHOLDER_IMAGE_GHOST

            size = module["size"] or 48
            image = (
                CircleImage(
                    name="sm_items-side-logo",
                    h_align="start",
                    v_align="start",
                    image_file=image_path.as_posix(),
                    size=size,
                )
                if module["rounded"]
                else Image(
                    name="sm_items-side-logo",
                    h_align="start",
                    v_align="start",
                    image_file=image_path.as_posix(),
                    size=size,
                )
            )

            button = Button(
                name="sm_items-side-button",
                h_align="start",
                v_align="fill",
                label=label,
                image=image,  # type: ignore
            )
            button.connect(
                "clicked", lambda _, b=button, n=name: self.on_button_clicked(b, n)
            )
            setup_cursor_hover(button)
            self.modules_box.add(button)
            self.buttons.append(button)
            self.button_by_name[name] = button

        self.scroll.add(self.modules_box)
        self.add(self.scroll)

    def on_button_clicked(self, clicked_button: Button, name: str):
        for btn in self.buttons:
            btn.remove_style_class("active")
        clicked_button.add_style_class("active")
        self.cfg.update_selection(name)

    def set_image_by(self, name: str, image_path: Path | str):
        image_path = Path(image_path)
        if name not in self.button_by_name:
            return
        for module in self.modules:
            if module["name"] == name:
                module["image-path"] = image_path
                break
        if not image_path.exists() or image_path.stat().st_size == 0:
            image_path = Const.PLACEHOLDER_IMAGE_GHOST
        button = self.button_by_name[name]
        image_widget = button.get_image()
        if hasattr(image_widget, "set_image_from_file"):
            image_widget.set_image_from_file(image_path.as_posix())
        elif hasattr(image_widget, "set_image"):
            image_widget.set_image(image_path.as_posix())
