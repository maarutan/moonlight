from typing import Optional
from fabric.widgets.eventbox import EventBox
from gi.repository import GLib, Gdk  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.stack import Stack
from fabric.widgets.button import Button
from fabric.utils.helpers import exec_shell_command_async as exec_cmd


class PopupMenu(EventBox):
    def __init__(self, items: Optional[list[dict]] = None):
        super().__init__(
            name="screen-popup-menu-eventbox",
            h_align="fill",
            v_align="fill",
            orientation="v",
        )

        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
        self.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.connect("leave-notify-event", self.on_leave)

        self.items = items or [
            {
                "icon": "",
                "name": "Empty Item",
                "cmd": "notify-send 'Empty item'",
            }
        ]

        children = []
        for item in self.items:
            btn = Button(
                h_align="fill",
                v_align="fill",
                name="screen-popup-menu-item",
                label=f"{item['icon']} {item['name']}",
            )
            btn.connect("clicked", lambda _, cmd=item["cmd"]: exec_cmd(cmd))
            children.append(btn)

        self.box = Box(name="screen-popup-menu", orientation="v")

        delay = 40

        def add_next_button(i=0):
            if i < len(children):
                self.box.add(children[i])
                children[i].show_all()
                GLib.timeout_add(delay, add_next_button, i + 1)
            return False

        GLib.timeout_add(delay, add_next_button)
        self.add(EventBox(child=self.box))

    def on_leave(self, widget, event):
        self.remove_style_class("screen-popup-menu-show")
        self.add_style_class("screen-popup-menu-hide")
        GLib.timeout_add(200, self.hide)
        return True
