from pathlib import Path
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from gi.repository import Gtk, GdkPixbuf  # type: ignore
from dataclasses import dataclass


@dataclass
class Types:
    TEXT: str = "text"
    IMAGE: str = "image"


class Logo(Button):
    def __init__(
        self,
        type_: str = Types.TEXT,
        content: str = "",
        image_path: str = "",
        image_size: int = 24,
    ):
        self._type = type_
        image_widget = None

        if image_path:
            image_path = image_path.replace("~", str(Path.home()))
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename=image_path,
                    width=image_size,
                    height=image_size,
                    preserve_aspect_ratio=True,
                )
                image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
            except Exception as e:
                print("[Logo] Failed to load image:", e)

        child_widget = None
        if content and self._type == Types.TEXT:
            child_widget = Label(label=content, name="logo-label")

        super().__init__(
            name="logo-container",
            image=image_widget if self._type == Types.IMAGE else None,
            child=child_widget if self._type == Types.TEXT else None,
        )

    def do_clicked(self, *args):
        print("[Logo] Clicked")
