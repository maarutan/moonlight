from pathlib import Path
from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from shared.blur_image import BlurImage
from shared.circular_image import CircleImage
from shared.file_picker import FilePicker
from utils.constants import Const
import os, getpass

if TYPE_CHECKING:
    from ...start_menu import StartMenu


class UserDashboardConfig(Box):
    def __init__(self, init_class: "StartMenu"):
        self.cfg = init_class
        super().__init__(
            name="sm_user-dashboard-config",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
        )

        avatar_path = Const.PROFILE_LOGO
        if not avatar_path.exists() or avatar_path.stat().st_size == 0:
            avatar_path = Const.PLACEHOLDER_IMAGE_GHOST

        self.blur = BlurImage(
            image_file=avatar_path.as_posix(),
            size=350,
            blur_radius=20,
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
        )

        self.avatar = CircleImage(
            image_file=avatar_path.as_posix(),
            size=220,
            h_align="center",
            v_align="center",
        )

        overlay = Overlay(
            name="sm_user-dashboard-overlay",
            child=self.blur,
        )
        overlay.add_overlay(self.avatar)

        username = Box(
            children=[
                Label(
                    name="sm_user-dashboard-definition",
                    label="- User: ",
                    h_align="fill",
                    v_align="start",
                ),
                Label(
                    name="sm_user-dashboard-description",
                    label=self.get_username(),
                    h_align="fill",
                    v_align="start",
                ),
            ]
        )
        hostname = Box(
            children=[
                Label(
                    name="sm_user-dashboard-definition",
                    label="- Host: ",
                    h_align="fill",
                    v_align="start",
                ),
                Label(
                    name="sm_user-dashboard-description",
                    label=self.get_hostname(),
                    h_align="fill",
                    v_align="start",
                ),
            ]
        )

        def handle_open(dialog):
            self.cfg.hide()

        def handle_close(dialog):
            self.cfg.show_all()

        self.file_picker = FilePicker(
            title="Select avatar",
            on_select=self.on_file_selected,
            h_align="center",
            v_align="center",
            on_close=handle_close,
            on_open=handle_open,
        )

        picker_box = Box(
            orientation="h",
            h_align="end",
            v_align="end",
            h_expand=True,
            v_expand=False,
            children=[self.file_picker],
        )
        overlay.add_overlay(picker_box)

        main_box = Box(
            orientation="v",
            spacing=16,
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            children=[
                overlay,
                username,
                hostname,
            ],
        )

        self.add(main_box)
        self.show_all()

    def get_username(self) -> str:
        try:
            return os.getlogin()
        except OSError:
            return getpass.getuser()

    def get_hostname(self) -> str:
        try:
            return os.uname().nodename
        except OSError:
            return "Unknown"

    def on_file_selected(self, file_path: str):
        self.avatar.set_image_from_file(file_path)
        self.blur.set_image(file_path)
        Const.PROFILE_LOGO.write_bytes(Path(file_path).read_bytes())
        self.cfg.items_side.set_image_by("user-dashboard", file_path)
