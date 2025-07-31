import math
from typing import cast
from gi.repository import Gtk, GdkPixbuf, cairo  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.label import Label
import re
import logging

logger = logging.getLogger(__name__)


class CustomImage(Gtk.Image):
    def __init__(self, image_path: str, icon_size: int = 64, **kwargs):
        super().__init__(**kwargs)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=image_path,
                width=icon_size,
                height=icon_size,
                preserve_aspect_ratio=True,
            )
            self.set_from_pixbuf(pixbuf)
        except Exception as e:
            logger.error(f"[CustomImage] Failed to load image '{image_path}': {e}")

    def do_render_rectangle(
        self, cr: cairo.Context, width: int, height: int, radius: int = 0
    ):
        cr.move_to(radius, 0)
        cr.line_to(width - radius, 0)
        cr.arc(width - radius, radius, radius, -(math.pi / 2), 0)
        cr.line_to(width, height - radius)
        cr.arc(width - radius, height - radius, radius, 0, (math.pi / 2))
        cr.line_to(radius, height)
        cr.arc(radius, height - radius, radius, (math.pi / 2), math.pi)
        cr.line_to(0, radius)
        cr.arc(radius, radius, radius, math.pi, (3 * (math.pi / 2)))
        cr.close_path()

    def do_draw(self, cr: cairo.Context):
        context = self.get_style_context()
        width, height = self.get_allocated_width(), self.get_allocated_height()
        cr.save()

        radius = cast(int, context.get_property("border-radius", Gtk.StateFlags.NORMAL))
        self.do_render_rectangle(cr, width, height, radius)
        cr.clip()
        super().do_draw(cr)

        cr.restore()
