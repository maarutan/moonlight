from pathlib import Path
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.eventbox import EventBox
from gi.repository import Gtk, Gdk  # type: ignore
from config import ASSETS
from utils import GetPreviewPath
from widgets import CircleImage
import gi

from config import PLACEHOLDER_IMAGE, URL_AVATAR, BACKBUTTON

gi.require_version("Gtk", "3.0")


class Logo(EventBox):
    def __init__(self, logo: dict, on_click=None, popup_active: bool = False):
        super().__init__(
            events=("enter-notify", "leave-notify", "button-press"),
            name="statusbar-profile-logo-button",
            h_align="center",
            v_align="center",
            h_expand=True,
            v_expand=True,
        )

        self.popup_active = popup_active
        self.hovered = False
        self.get_preview = GetPreviewPath()
        self.inner_box = Box(orientation="horizontal", spacing=0)
        self.add(self.inner_box)

        logo_type = logo.get("type", "text")
        content = logo.get("content", "")
        image_cfg = logo.get("image", {})
        self.image_collapse_path = str(image_cfg.get("collapse-image", None)).format(
            assets=ASSETS.as_posix()
        )

        image_path = image_cfg.get("path", PLACEHOLDER_IMAGE.as_posix())
        self.collapse_icon = logo.get("collapse-icon", "󱞥")
        self.collapse_type = logo.get("collapse-type", "text")
        self.image_size = image_cfg.get("size", 38)
        image_shape = image_cfg.get("shape", "circle")
        self._image_shape = image_shape
        self.logo_type = logo_type

        if logo_type == "image":
            path = Path(image_path).expanduser()

            if not path.exists() and image_path.startswith(("http://", "https://")):
                if not URL_AVATAR.exists() and self.get_preview.is_image_url(
                    image_path
                ):
                    path = self.get_preview.download_and_cache_image(
                        url=image_path, result=URL_AVATAR
                    )
                else:
                    path = URL_AVATAR if URL_AVATAR.exists() else PLACEHOLDER_IMAGE
            elif not path.exists():
                path = PLACEHOLDER_IMAGE

            widget_class = CircleImage if image_shape == "circle" else Image
            self.normal_image = widget_class(
                name="statusbar-profile-logo-image",
                h_align="center",
                image_file=str(path),
                size=self.image_size,
            )

            if self.collapse_type == "image":
                collapse_path_raw = self.image_collapse_path or BACKBUTTON.as_posix()
                collapse_path = Path(collapse_path_raw).expanduser()

                if collapse_path_raw.startswith(("http://", "https://")):
                    collapse_cache_path = (
                        URL_AVATAR.parent / Path(collapse_path_raw).name
                    )
                    if (
                        not collapse_cache_path.exists()
                        and self.get_preview.is_image_url(collapse_path_raw)
                    ):
                        collapse_path = self.get_preview.download_and_cache_image(
                            url=collapse_path_raw, result=collapse_cache_path
                        )
                    else:
                        collapse_path = (
                            collapse_cache_path
                            if collapse_cache_path.exists()
                            else BACKBUTTON
                        )
                else:
                    if not collapse_path.exists():
                        collapse_path = BACKBUTTON

                self.collapse_image = widget_class(
                    name="statusbar-profile-logo-image-collapse",
                    h_align="center",
                    image_file=str(collapse_path),
                    size=self.image_size,
                )
            else:
                collapse_content = self.collapse_icon
                if " " not in collapse_content:
                    collapse_content = collapse_content.center(len(content))
                self.collapse_image = Label(
                    label=collapse_content, name="logo-label-collapse"
                )

        elif logo_type == "text" and content:
            self.normal_image = Label(label=content, name="logo-label")
            collapse_content = self.collapse_icon
            if " " not in collapse_content:
                collapse_content = collapse_content.center(len(content))
            self.collapse_image = Label(
                label=collapse_content, name="logo-label-collapse"
            )

        self._apply_collapse(self.popup_active)
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)
        if on_click:
            self.connect("button-press-event", lambda *a: on_click())

    def _apply_collapse(self, hover: bool):
        self.inner_box.foreach(lambda w: self.inner_box.remove(w))
        widget_to_show = (
            self.collapse_image if self.popup_active or hover else self.normal_image
        )
        self.inner_box.pack_start(widget_to_show, True, True, 0)
        self.show_all()

    def set_popup_active(self, active: bool):
        self.popup_active = bool(active)
        self._apply_collapse(True if self.popup_active else self.hovered)

    def _on_enter(self, widget, event):
        display = Gdk.Display.get_default()
        cursor = Gdk.Cursor.new_from_name(display, "pointer")
        widget.get_window().set_cursor(cursor)
        self.hovered = True
        if not self.popup_active:
            self._apply_collapse(True)

    def _on_leave(self, widget, event):
        widget.get_window().set_cursor(None)
        self.hovered = False
        if not self.popup_active:
            self._apply_collapse(False)
