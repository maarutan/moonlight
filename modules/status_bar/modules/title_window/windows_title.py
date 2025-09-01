from config import RESOLVED_ICONS
from utils import WINDOW_TITLE_MAP
from typing import Literal, Optional
import unicodedata
import re

from fabric.widgets.image import Image
from fabric.utils import truncate
import gi
from fabric.widgets.box import Box
from fabric.widgets.label import Label

from utils import IconResolver
from fabric.hyprland.service import Hyprland, HyprlandEvent

gi.require_version("Gtk", "3.0")


class WindowsTitle(Box):
    def __init__(
        self,
        is_horizontal: bool = True,
        truncation: bool = True,
        truncation_size: int = 80,
        title_type: Literal["class", "title"] = "title",
        title_type_length: int = 30,
        title_map: Optional[list] = None,
        title_exceptions: Optional[list] = None,
        vertical_title_length: int = 6,
        enable_icon: bool = True,
        resolve_icon: bool = True,
        resolve_icon_size: int = 16,
        resolve_position: Literal["left", "right"] = "left",
    ):
        self.title_type = title_type
        self.title_type_length = title_type_length
        self.resolve_position = resolve_position
        self.resolve_icon_size = resolve_icon_size
        self.title_exceptions = title_exceptions or []
        self.resolve_icon = resolve_icon
        self.enable_icon = enable_icon
        self.icon = IconResolver(RESOLVED_ICONS)
        self.is_horizontal = is_horizontal
        self.vertical_title_length = vertical_title_length
        self.truncation = truncation
        self.truncation_size = truncation_size
        self.title_map = title_map or []
        self.merged_titles = self.title_map + WINDOW_TITLE_MAP

        super().__init__(
            v_expand=True,
            h_expand=True,
            v_align="center",
            h_align="center",
        )

        self.add(self._build_container("", ""))

        def on_active_window(_, event: HyprlandEvent):
            win_class = event.data[0] or ""
            win_title = event.data[1] or ""
            self.children = self._build_container(win_class, win_title)

        self.hypr = Hyprland(commands_only=False)
        self.hypr.connect("event::activewindow", on_active_window)

    def _match_exception(self, win_class: str, win_title: str):
        win_class_l = win_class.lower()
        win_title_l = win_title.lower()
        return next(
            (
                ex
                for ex in self.title_exceptions
                if re.search(ex[0].lower(), win_class_l)
                or re.search(ex[0].lower(), win_title_l)
            ),
            None,
        )

    def _trim_visual(self, text: str, max_width: int) -> str:
        result = ""
        current_width = 0
        for char in text:
            char_width = 2 if unicodedata.east_asian_width(char) in ("F", "W") else 1
            if current_width + char_width > max_width:
                break
            result += char
            current_width += char_width
        return result

    def _get_title_and_icon(self, win_class: str, win_title: str):
        matched_exception = self._match_exception(win_class, win_title)
        if matched_exception:
            icon_text = matched_exception[1]
            title_text = matched_exception[2]
            if not self.is_horizontal:
                icon_text = self._trim_visual(icon_text, 1)
                title_text = self._trim_visual(title_text, self.vertical_title_length)
            return title_text, icon_text

        matched_window = next(
            (
                wt
                for wt in self.merged_titles
                if re.search(wt[0].lower(), win_class.lower())
            ),
            None,
        )

        if matched_window:
            icon_text = matched_window[1] if not self.resolve_icon else ""
            window_class_title = matched_window[2]
        else:
            icon_text = "" if not self.resolve_icon else ""
            window_class_title = win_class.lower() or "unknown"

        if self.title_type == "title":
            display_text = win_title
        else:
            display_text = window_class_title

        if not self.is_horizontal:
            display_text = self._trim_visual(display_text, self.vertical_title_length)
        elif self.title_type_length > 0:
            display_text = truncate(display_text, self.title_type_length)

        if self.enable_icon:
            if self.resolve_icon:
                pixbuf = self.icon.get_icon_pixbuf(win_class, self.resolve_icon_size)
                return display_text, pixbuf
            else:
                return display_text, icon_text
        else:
            return display_text, ""

    def _build_container(self, win_class: str, win_title: str) -> Box:
        container = Box(
            name="statusbar-windows-title-box",
            orientation="h" if self.is_horizontal else "v",
            h_align="center",
            v_align="center",
            h_expand=True,
            v_expand=True,
        )

        text, icon_or_pixbuf = self._get_title_and_icon(win_class, win_title)

        if isinstance(icon_or_pixbuf, str) and icon_or_pixbuf:
            if self.is_horizontal:
                if self.resolve_position == "left":
                    container.add(
                        Label(
                            f" {icon_or_pixbuf} ",
                            h_align="center",
                            v_align="center",
                            h_expand=True,
                            v_expand=True,
                        )
                    )
                    container.add(Label(text))
                else:
                    container.add(Label(text))
                    container.add(Label(icon_or_pixbuf))
            else:
                icon_trimmed = self._trim_visual(icon_or_pixbuf, 1)
                text_trimmed = self._trim_visual(text, self.vertical_title_length)
                container.add(
                    Label(
                        icon_trimmed,
                        h_align="center",
                        v_align="center",
                        h_expand=True,
                        v_expand=True,
                    ),
                )
                container.add(Label(text_trimmed))
        elif icon_or_pixbuf:
            label = Label(text)
            if self.is_horizontal:
                if self.resolve_position == "left":
                    container.add(Image(pixbuf=icon_or_pixbuf))
                    container.add(label)
                else:
                    container.add(label)
                    container.add(Image(pixbuf=icon_or_pixbuf))
            else:
                container.add(Image(pixbuf=icon_or_pixbuf))
                container.add(label)
        else:
            container.add(Label(text))

        return container
