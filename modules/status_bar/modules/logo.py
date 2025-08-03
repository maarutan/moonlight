from pathlib import Path
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from gi.repository import Gtk, GdkPixbuf, Gdk  # type: ignore
from dataclasses import dataclass


@dataclass
class Types:
    TEXT: str = "text"
    IMAGE: str = "image"


class Logo(Box):
    def __init__(
        self,
        type: str = Types.TEXT,
        content: str = "",
        image_path: str = "",
        image_size: int = 24,
        is_horizontal: bool = True,
    ):
        self._type = type
        self.image_widget = None

        if image_path:
            image_path = image_path.replace("~", str(Path.home()))
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename=image_path,
                    width=image_size,
                    height=image_size,
                    preserve_aspect_ratio=True,
                )
                self.image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
            except Exception as e:
                print("[Logo] Failed to load image:", e)

        child_widget = None
        if content and self._type == Types.TEXT:
            child_widget = Label(label=content, name="logo-label")

        self.button = Button(
            name="logo-button",
            image=self.image_widget if self._type == Types.IMAGE else None,
            child=child_widget if self._type == Types.TEXT else None,
            on_clicked=self.do_clicked,
        )

        super().__init__(
            name="logo-container",
            orientation="h" if is_horizontal else "v",
            children=self.button,
        )

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self._on_box_click)

    def _on_box_click(self, widget, event):
        self.button.emit("clicked")
        return True

    def do_clicked(self, *args):
        print("[Logo] Clicked")
