from typing import TYPE_CHECKING, Optional
from fabric.utils import GdkPixbuf
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from utils.colors_parse import colors
from fabric.widgets.svg import Svg


if TYPE_CHECKING:
    from .core import NotifyCore
    from fabric.notifications import Notification  # type: ignore


class ImagesHandler(Box):
    def __init__(self, class_init: "NotifyCore"):
        self.conf = class_init
        self.notif = self.conf._notification

        super().__init__(
            name="image",
            orientation="h",
        )
        if _build_image := self._build_image():
            self.add(_build_image)
        else:
            self.add(self._build_svg_urgency_handler())

    def _build_image(self) -> Image | None:
        if getattr(self.notif, "image_pixbuf", None):
            pb = self.notif.image_pixbuf
            return Image(
                name="n_image",
                pixbuf=pb.scale_simple(
                    self.conf.notify_widget.confh.config["image-size"],
                    self.conf.notify_widget.confh.config["image-size"],
                    GdkPixbuf.InterpType.BILINEAR,
                ),
            )
        if getattr(self.notif, "image_file", None):
            return Image(
                name="n_image",
                pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_size(
                    self.notif.image_file,
                    self.conf.notify_widget.confh.config["image-size"],
                    self.conf.notify_widget.confh.config["image-size"],
                ),
            )

        if getattr(self.notif, "app_icon", None):
            return Image(
                name="n_image",
                pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_size(
                    self.notif.app_icon,
                    self.conf.notify_widget.confh.config["image-size"],
                    self.conf.notify_widget.confh.config["image-size"],
                ),
            )

    def update(self, new_notification: "Notification") -> None:
        self.notif = new_notification
        pixbuf = self._build_pixbuf()
        try:
            self.pixbuf = pixbuf
        except Exception:
            if pixbuf is None:
                try:
                    self.image_file = None
                except Exception:
                    pass

    def _build_svg_urgency_handler(self) -> Svg:
        ur = str(self.notif.do_get_hint_entry("urgency"))
        if ur == "1":
            icon = f"""
                <svg height="640" version="1.1" viewBox="0 0 640 640" width="640" xmlns="http://www.w3.org/2000/svg">
                  <g id="icomoon-ignore"></g>
                  <path d="M320 12.8c-169.696 0-307.232 137.536-307.232 307.2 0 169.696 137.536 307.232 307.232 307.232 169.632 0 307.2-137.536 307.2-307.232 0-169.664-137.568-307.2-307.2-307.2zM348.672 123.712c29.952 0 38.752 17.376 38.752 37.248 0 24.8-19.84 47.744-53.728 47.744-28.352 0-41.856-14.24-41.024-37.824 0-19.872 16.608-47.168 56-47.168zM271.936 504c-20.48 0-35.424-12.448-21.12-67.008l23.456-96.8c4.064-15.488 4.736-21.696 0-21.696-6.112 0-32.704 10.688-48.384 21.248l-10.208-16.736c49.76-41.568 106.976-65.952 131.456-65.952 20.48 0 23.872 24.192 13.664 61.44l-26.88 101.76c-4.768 17.984-2.72 24.192 2.048 24.192 6.144 0 26.24-7.424 46.016-23.008l11.584 15.552c-48.416 48.384-101.184 67.008-121.632 67.008z" fill="{colors["blue"]}"></path>
                </svg>
            """

        elif ur == "2":
            icon = f"""
                <svg height="448" version="1.1" viewBox="0 0 416 448" width="416" xmlns="http://www.w3.org/2000/svg">
                  <g id="icomoon-ignore"></g>
                  <path d="M408 240c0 8.75-7.25 16-16 16h-56c0 31.25-6.75 54.75-16.75 72.5l52 52.25c6.25 6.25 6.25 16.25 0 22.5-3 3.25-7.25 4.75-11.25 4.75s-8.25-1.5-11.25-4.75l-49.5-49.25s-32.75 30-75.25 30v-224h-32v224c-45.25 0-78.25-33-78.25-33l-45.75 51.75c-3.25 3.5-7.5 5.25-12 5.25-3.75 0-7.5-1.25-10.75-4-6.5-6-7-16-1.25-22.75l50.5-56.75c-8.75-17.25-14.5-39.5-14.5-68.5h-56c-8.75 0-16-7.25-16-16s7.25-16 16-16h56v-73.5l-43.25-43.25c-6.25-6.25-6.25-16.25 0-22.5s16.25-6.25 22.5 0l43.25 43.25h211l43.25-43.25c6.25-6.25 16.25-6.25 22.5 0s6.25 16.25 0 22.5l-43.25 43.25v73.5h56c8.75 0 16 7.25 16 16zM288 96h-160c0-44.25 35.75-80 80-80s80 35.75 80 80z" fill="{colors["red"]}"></path>
                </svg>
            """
        else:
            icon = f"""
                <svg height="1024" version="1.1" viewBox="0 0 1024 1024" width="1024" xmlns="http://www.w3.org/2000/svg">
                  <g id="icomoon-ignore"></g>
                  <path d="M907.5 755.1l-345.1-558.4c-27.8-44.9-73-45-100.8 0v0l-345.1 558.4c-37.3 60.3-10.2 108.9 60.4 108.9h670.2c70.5 0 97.6-48.7 60.4-108.9zM512 768c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32zM544 608.1c0 17.4-14.3 31.9-32 31.9-17.8 0-32-14.3-32-31.9v-192.2c0-17.4 14.3-31.9 32-31.9v0c17.8 0 32 14.3 32 31.9v192.2z" fill="{colors["yellow"]}"></path>
                </svg>
            """
        return Svg(
            name="n_urgency",
            svg_string=icon,
            size=self.conf.notify_widget.confh.config["urgency-size"],
        )
