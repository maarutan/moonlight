# input.py
from fabric.widgets.box import Box
from shared.animated_entry import Entry
from fabric.utils.helpers import idle_add
from utils.colors_parse import colors


class ALInput(Box):
    def __init__(self):
        super().__init__(
            name="al_input",
            orientation="v",
            h_align="start",
            h_expand=False,
        )

        self.entry = Entry(
            name="al_entry",
            placeholder="find an app",
            h_align="fill",
            h_expand=True,
        )

        self.entry.set_caret_boldness(2)
        self.entry.set_caret_color_hex(colors["text"])
        idle_add(lambda: self.entry.grab_focus())

        self.add(self.entry)

    def set_fixed_width(self, width: int):
        try:
            self.set_min_content_width(width)
        except Exception:
            pass
