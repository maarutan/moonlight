# input.py
from fabric.utils import Gdk
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

        self.entry.set_property("activates-default", False)
        self.entry.set_property("has-frame", True)
        self.entry.connect("focus-in-event", lambda w, e: True)

        idle_add(lambda: self.entry.grab_focus())

        self.add(self.entry)
