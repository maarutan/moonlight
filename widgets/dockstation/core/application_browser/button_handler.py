from typing import TYPE_CHECKING, Optional
from fabric.utils import DesktopApp
from fabric.widgets.button import Button
from shared.app_icon import AppIcon
from utils.widget_utils import setup_cursor_hover
from ..dock_items.appcontextmenu import AppContextMenu

if TYPE_CHECKING:
    from .browser import ApplicationBrowser


class ButtonHandler:
    def __init__(
        self, app_browser: "ApplicationBrowser", app: DesktopApp, index: int = 0
    ):
        self.app = app
        self.app_browser = app_browser
        self.menu: Optional[object] = None
        self.btn: Optional[Button] = None
        self.btn = self.make_btn(index)

    def make_btn(self, index: int) -> Button:
        display_name = self.app.display_name or ""
        description = self.app.description or ""
        btn = Button(
            name="dockstation-btn",
            v_align="start",
            h_align="center",
            h_expand=True,
            v_expand=False,
            style_classes=["dockstation-btn-appbrowser"],
            child=AppIcon(app_name=str(display_name), icon_size=48),
            tooltip_text=str(description),
        )
        setup_cursor_hover(btn)
        btn.connect("button-press-event", self.on_click)
        return btn

    def on_click(self, widget, event):
        if event.button == 3:
            try:
                from ..dock_items.appcontextmenu import AppContextMenu

                if self.menu is None:
                    self.menu = AppContextMenu(
                        self.app_browser.dockstation, str(self.app.icon_name)
                    )
                if self.menu is not None:
                    self.menu.popup(widget)  # type: ignore
            except Exception:
                pass
            return True
        if event.button == 1:
            try:
                self.app_browser.dockstation.actions.handle_app(
                    str(self.app.icon_name), []
                )
            except Exception:
                pass
            try:
                if self.menu is not None:
                    self.menu.menu.popdown()  # type: ignore
            except Exception:
                pass
            return True
        return False
