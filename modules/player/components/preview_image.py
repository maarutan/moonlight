import gi

from typing import Optional
from utils import GetPreviewPath
from loguru import logger

from fabric.widgets.image import Image
from fabric.widgets.box import Box
from gi.repository import Gtk  # type:ignore

gi.require_version("Gdk", "3.0")


class PlayerPreviewImage(Box):
    def __init__(
        self,
        player_image_preview_path: Optional[str] = None,
    ):
        self.path = player_image_preview_path
        self._get_preview_path = GetPreviewPath()

        super().__init__(
            name="preview_image",
            orientation=Gtk.Orientation.HORIZONTAL,
            h_align="center",
            v_align="center",
            children=self._make_image(),
        )

    def _make_image(self) -> Image | None:
        try:
            image_widget = Image(
                image_file=str(
                    self._get_preview_path.validator(self.path if self.path else "")
                ),
                size=(360, 360),
                # h_align="center",
                # v_align="center",
                # h_expand=True,
                # v_expand=True,
            )
            image_widget.show_all()
            return image_widget
        except Exception as e:
            logger.warning(f"[PlayerPopup] Failed to load image: {e}")
            return None
