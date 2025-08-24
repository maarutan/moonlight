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
        title_map: Optional[list] = None,
        title_exceptions: Optional[list] = None,
        vertical_title_length: int = 6,
        enable_icon: bool = True,
        resolve_icon: bool = True,
        resolve_icon_size: int = 16,
        resolve_position: Literal["left", "right"] = "left",
    ):
        self.resolve_position = resolve_position
        self.resolve_icon_size = resolve_icon_size
        self.title_exceptions = title_exceptions or []
        self.resolve_icon = resolve_icon
        self.enable_icon = enable_icon
        self.icon = IconResolver(RESOLVED_ICONS)
        self.is_horizontal = is_horizontal
        self.vertical_title_length = vertical_title_length
        self.current_title = None
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
        return next(
            (
                ex
                for ex in self.title_exceptions
                if re.search(ex[0], win_class, re.IGNORECASE)
                or re.search(ex[0], win_title, re.IGNORECASE)
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
            (wt for wt in self.merged_titles if re.search(wt[0], win_class.lower())),
            None,
        )

        if matched_window:
            icon_text = matched_window[1] if not self.resolve_icon else ""
            title_text = matched_window[2]
        else:
            icon_text = "" if not self.resolve_icon else ""
            title_text = win_class.lower() or "unknown"

        if self.truncation and self.is_horizontal:
            title_text = truncate(title_text, self.truncation_size)
        elif not self.is_horizontal:
            title_text = self._trim_visual(title_text, self.vertical_title_length)

        if self.resolve_icon and self.enable_icon:
            pixbuf = self.icon.get_icon_pixbuf(win_class, self.resolve_icon_size)
            return title_text, pixbuf
        else:
            return title_text, icon_text

    def _build_container(self, win_class: str, win_title: str) -> Box:
        container = Box(
            name="statusbar-windows-title-box",
            orientation="h" if self.is_horizontal else "v",
        )

        text, icon_or_pixbuf = self._get_title_and_icon(win_class, win_title)

        if isinstance(icon_or_pixbuf, str) and icon_or_pixbuf:
            label = Label(text)
            icon_label = Label(icon_or_pixbuf)
            if self.resolve_position == "left":
                container.add(icon_label)
                container.add(label)
            else:
                container.add(label)
                container.add(icon_label)
        elif icon_or_pixbuf:
            image = Image(pixbuf=icon_or_pixbuf)
            label = Label(text)
            if self.resolve_position == "left":
                container.add(image)
                container.add(label)
            else:
                container.add(label)
                container.add(image)
        else:
            container.add(Label(text))

        return container
