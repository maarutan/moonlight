from .dockstation.dock import DockStation
from .statusbar.bar import StatusBar
from .notification.notify_widget import NotificationWidget
from .languagepreview.language_widget import LanguagePreview
from .activatelinux.linux_widget import ActivateLinux
from .screencorners.corners import ScreenCorners
from .desktop.desktop import Desktop


WIDGETS = [
    ScreenCorners,
    StatusBar,
    DockStation,
    NotificationWidget,
    LanguagePreview,
    ActivateLinux,
    Desktop,
]
