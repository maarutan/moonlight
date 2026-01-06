from fabric.widgets.window import Window
from fabric.widgets.box import Box
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.entry import Entry
from fabric.utils import Gtk, get_desktop_applications, DesktopApp
from utils.widget_utils import setup_cursor_hover


class ApplicationBrowser(Box):
    def __init__(self):
        super().__init__(
            name="dockstation-app-browser",
        )
        self.scroll = ScrolledWindow()
