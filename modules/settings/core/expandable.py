from typing import Optional
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from shared.expandable import CollapsibleBox
from fabric.utils.helpers import Gtk


class Expandable(Box):
    def __init__(
        self,
        name: str,
        widget: Box,
    ):
        self.body = EventBox(child=EventBox(child=widget))

        self.expandable_box = CollapsibleBox(
            title=name,
            name="sm_expandable_collapsible",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            child=self.body,
        )

        self.wrapper = EventBox(
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            child=self.expandable_box,
        )

        super().__init__(
            name="sm_expandable",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            children=self.wrapper,
        )
