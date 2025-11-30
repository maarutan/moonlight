from pathlib import Path
from typing import TYPE_CHECKING
from fabric.utils import Gtk
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from shared.blur_image import BlurImage
from shared.circular_image import CircleImage
from shared.file_picker import FilePicker
from fabric.widgets.eventbox import EventBox
from utils.constants import Const
from shared.expandable import CollapsibleBox

if TYPE_CHECKING:
    from ....start_menu import StartMenu


from .modules.bar_core import StatusBarConfig

from ...expandable import Expandable


class ApplicationConfig(Box):
    def __init__(self, init_class: "StartMenu"):
        self.cfg = init_class
        super().__init__(
            name="application-config",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
        )

        avatar_path = Const.APP_ICONS_DIRECTORY / "app.svg"
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

        main_box = Box(
            orientation="v",
            spacing=16,
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            children=[
                overlay,
                Expandable(
                    name="Status Bar",
                    widget=StatusBarConfig(self),
                ),
                Expandable(
                    name="Status Bar",
                    widget=StatusBarConfig(self),
                ),
            ],
        )

        self.add(main_box)
        self.show_all()
