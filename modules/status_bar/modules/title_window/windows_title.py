# windows_title.py

from utils import WINDOW_TITLE_MAP
from typing import Optional
import unicodedata
import re

from fabric.utils import FormattedString, truncate  # type: ignore
from fabric.hyprland.widgets import ActiveWindow
from fabric.widgets.box import Box


class WindowsTitle(Box):
    """A widget that displays the title of the active window."""

    def __init__(
        self,
        orientation_pos: bool = True,
        truncation: bool = True,
        truncation_size: int = 80,
        title_map: Optional[list] = None,
        vertical_title_length: int = 6,
        enable_icon: bool = True,
        **kwargs,
    ):
        self.orientation_pos = orientation_pos
        self.truncation = truncation
        self.truncation_size = truncation_size
        self.title_map = title_map or []
        self.enable_icon = enable_icon
        self.vertical_title_length = vertical_title_length
        self.merged_titles = self.title_map + WINDOW_TITLE_MAP
        super().__init__(name="window-box", **kwargs)

        self.children = Box(
            children=[
                ActiveWindow(
                    name="window",
                    formatter=FormattedString(
                        "{ get_title(win_title, win_class) }",
                        get_title=self._get_title,
                    ),
                )
            ]
        )

    def _trim_visual(self, text: str, max_width: int) -> str:
        result = ""
        current_width = 0
        for char in text:
            if unicodedata.east_asian_width(char) in ("F", "W"):
                char_width = 2
            else:
                char_width = 1

            if current_width + char_width > max_width:
                break

            result += char
            current_width += char_width

        return result

    def _get_title(self, win_title, win_class):
        if self.truncation:
            win_title = truncate(win_title, self.truncation_size)

        win_class_lower = win_class.lower()

        matched_window = next(
            (wt for wt in self.merged_titles if re.search(wt[0], win_class_lower)),
            None,
        )

        if not matched_window:
            not_matched_window_icon = ""
            not_matched_window = win_class_lower
            if self.orientation_pos:
                return f"{not_matched_window_icon} {not_matched_window}"
            else:
                not_matched_window = self._trim_visual(
                    not_matched_window, self.vertical_title_length
                )
                return f" {not_matched_window_icon}\n{not_matched_window}."

        title = matched_window[2]
        icon = matched_window[1]

        if not self.enable_icon:
            return title

        if self.orientation_pos:
            return f"{icon} {title}"
        else:
            title = self._trim_visual(title, self.vertical_title_length)
            return f" {icon}\n{title}."
