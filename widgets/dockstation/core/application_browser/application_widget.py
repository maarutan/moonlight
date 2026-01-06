import logging
from typing import TYPE_CHECKING
from fabric.utils import GLib, Gtk
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.revealer import Revealer
from .browser import ApplicationBrowser

if TYPE_CHECKING:
    from ...dock import DockStation

TIMEOUT = (500, 300)


class ApplicationBrowserWidget(Revealer):
    def __init__(self, dockstation: "DockStation"):
        self.dockstation = dockstation
        self._hide_timeout_id = None
        self._show_timeout_id = None

        self.app_browser = ApplicationBrowser(dockstation)
        super().__init__(
            child=self.app_browser,
            reveal_child=False,
            transition_type=self._transition_handler(),
            transition_duration=TIMEOUT[0],
            h_expand=True,
            v_expand=True,
        )
        self.hide()

        self.is_hover = False

        def on_enter(widget, event):
            self.is_hover = True

        def on_leave(widget, event):
            self.is_hover = False

        self.app_browser.connect("enter-notify-event", on_enter)
        self.app_browser.connect("leave-notify-event", on_leave)

    def toggle(self, hamburger=None):
        if self.child_revealed:
            self.on_hide(hamburger)
        else:
            self.on_show(hamburger)

    def on_show(self, hamburger=None):
        self.dockstation.exclusivity = "none"

        self.show()
        if self._show_timeout_id is not None:
            GLib.source_remove(self._show_timeout_id)
            self._show_timeout_id = None

        self._show_timeout_id = GLib.timeout_add(
            TIMEOUT[1], lambda: self._show_revealer(hamburger=hamburger)
        )

    def on_hide(self, hamburger=None):
        if self.dockstation.confh.config["auto-hide"]:
            self.dockstation.exclusivity = "none"

        if self._hide_timeout_id is not None:
            GLib.source_remove(self._hide_timeout_id)
            self._hide_timeout_id = None

        if hamburger is not None:
            hamburger.on_deactivate()
        self.unreveal()
        self._hide_timeout_id = GLib.timeout_add(
            TIMEOUT[0], self._hide_revealer, hamburger
        )

    def _hide_revealer(self, *args, hamburger=None):
        if self.dockstation.confh.config["auto-hide"]:
            ...
        else:
            self.dockstation.exclusivity = "auto"
        self.hide()
        self._hide_timeout_id = None
        if hamburger is not None:
            hamburger.on_deactivate()
        return False

    def _show_revealer(self, *args, hamburger=None):
        self.reveal()
        if hamburger is not None:
            hamburger.on_activate()
        self._show_timeout_id = None
        return False

    def _transition_handler(self) -> Gtk.RevealerTransitionType:
        anchor = self.dockstation.confh.config.get("anchor", "").lower()
        fade = Gtk.RevealerTransitionType.CROSSFADE
        left = Gtk.RevealerTransitionType.SLIDE_LEFT
        right = Gtk.RevealerTransitionType.SLIDE_RIGHT
        top = Gtk.RevealerTransitionType.SLIDE_UP
        bottom = Gtk.RevealerTransitionType.SLIDE_DOWN

        if "left" in anchor:
            return right
        if "right" in anchor:
            return left
        if "top" in anchor:
            return bottom
        if "bottom" in anchor:
            return top
        return fade
