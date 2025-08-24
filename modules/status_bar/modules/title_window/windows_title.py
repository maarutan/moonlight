from config import RESOLVED_ICONS
from utils import WINDOW_TITLE_MAP
from typing import Optional
import unicodedata
import re

from fabric.widgets.image import Image
from fabric.utils import truncate
import gi
from gi.repository import Gtk  # type: ignore
from fabric.hyprland.widgets import ActiveWindow
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
        icon_resolve: bool = True,
        icon_size: int = 16,
        **kwargs,
    ):
        self.icon_size = icon_size
        self.title_exceptions = title_exceptions or []
        self.icon_resolve = icon_resolve
        self.icon = IconResolver(RESOLVED_ICONS)
        self.is_horizontal = is_horizontal
        self.current_title = None
        self.truncation = truncation
        self.truncation_size = truncation_size
        self.title_map = title_map or []
        self.enable_icon = enable_icon
        self.vertical_title_length = vertical_title_length
        self.merged_titles = self.title_map + WINDOW_TITLE_MAP

        super().__init__(
            v_expand=True,
            h_expand=True,
            v_align="center",
            h_align="center",
            **kwargs,
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

    def _build_container(self, win_class: str, win_title: str) -> Box:
        container = Box(
            name="statusbar-windows-title-box",
            orientation="h" if self.is_horizontal else "v",
        )

        matched_exception = self._match_exception(win_class, win_title)

        if matched_exception:
            icon_text = matched_exception[1]
            title_text = matched_exception[2]
            if self.is_horizontal:
                container.add(Label(f"{icon_text} {title_text}"))
            else:
                icon_text = self._trim_visual(icon_text, 1)
                title_text = self._trim_visual(title_text, self.vertical_title_length)
                container.add(Label(f"{icon_text}\n{title_text}"))
            return container

        if self.icon_resolve:
            pixbuf = self.icon.get_icon_pixbuf(win_class, self.icon_size)
            if pixbuf:
                container.add(Image(pixbuf=pixbuf))
        container.add(Label(self._get_title(win_title, win_class)))
        return container

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

    def _get_title(self, win_title: str, win_class: str) -> str:
        if self.truncation:
            win_title = truncate(win_title, self.truncation_size)

        win_class_lower = win_class.lower()
        matched_exception = self._match_exception(win_class, win_title)

        if matched_exception:
            title = matched_exception[2]
            icon = matched_exception[1] if not self.icon_resolve else ""
            if not self.enable_icon:
                return title
            if self.is_horizontal:
                return f"{icon} {title}"
            else:
                title = self._trim_visual(title, self.vertical_title_length)
                return f" {icon}\n{title}."

        matched_window = next(
            (wt for wt in self.merged_titles if re.search(wt[0], win_class_lower)),
            None,
        )

        if not matched_window:
            not_matched_window_icon = ""
            not_matched_window = win_class_lower or "unknown"
            if self.is_horizontal:
                return f"{not_matched_window_icon} {not_matched_window}"
            else:
                not_matched_window = self._trim_visual(
                    not_matched_window, self.vertical_title_length
                )
                return f" {not_matched_window_icon}\n{not_matched_window}."

        title = matched_window[2]
        icon = matched_window[1] if not self.icon_resolve else ""
        if not self.enable_icon:
            return title
        if self.is_horizontal:
            return f"{icon} {title}"
        else:
            title = self._trim_visual(title, self.vertical_title_length)
            return f" {icon}\n{title}."
