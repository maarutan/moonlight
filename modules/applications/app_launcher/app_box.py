from typing import Iterator, List, Optional
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler


class AppsBox(Box):
    def __init__(self, all_apps: List[DesktopApp] | None = None, spacing: int = 6):
        super().__init__(name="al_apps-box", orientation="v", spacing=spacing)
        self._arranger_handler: int = 0
        self._all_apps = (
            all_apps if all_apps is not None else get_desktop_applications()
        )

        self._last_filtered: List[DesktopApp] = []

    def arrange_viewport(self, query: str = "") -> bool:
        remove_handler(self._arranger_handler) if self._arranger_handler else None
        self.children = []

        filtered = [
            app
            for app in self._all_apps
            if query.casefold()
            in (
                (app.display_name or "")
                + (" " + (app.name or "") + " ")
                + (app.generic_name or "")
            ).casefold()
        ]

        self._last_filtered = filtered

        filtered_iter: Iterator[DesktopApp] = iter(filtered)
        should_resize = len(filtered) == len(self._all_apps)

        self._arranger_handler = idle_add(
            lambda *args: self._add_next_application(*args)
            or (self._resize_viewport() if should_resize else False),
            filtered_iter,
            pin=True,
        )
        return False

    def _add_next_application(self, apps_iter: Iterator[DesktopApp]) -> bool:
        app = next(apps_iter, None)
        if not app:
            return False
        self.add(self._bake_application_slot(app))
        return True

    def _resize_viewport(self) -> bool:
        try:
            parent = self.get_parent()
            if hasattr(parent, "set_min_content_width"):
                parent.set_min_content_width(self.get_allocation().width)  # type: ignore
        except Exception:
            pass
        return False

    def _find_launcher_in_parents(self) -> Optional[object]:
        try:
            parent = self.get_parent()
            while parent is not None:
                if hasattr(parent, "tools") and hasattr(parent.tools, "close"):
                    return parent
                parent = parent.get_parent()
        except Exception:
            pass
        return None

    def _bake_application_slot(self, app: DesktopApp, **kwargs) -> Button:
        def _on_clicked(*_):
            try:
                app.launch()
            except Exception:
                return
            if getattr(self, "application", None):
                try:
                    self.application.quit()
                except Exception:
                    pass
            launcher = self._find_launcher_in_parents()
            if launcher is not None:
                try:
                    launcher.tools.close()
                except Exception:
                    try:
                        launcher.tools.force_close()
                    except Exception:
                        pass

        return Button(
            name="al_app-slot",
            child=Box(
                orientation="h",
                spacing=12,
                children=[
                    Image(pixbuf=app.get_icon_pixbuf(), h_align="start", size=32),
                    Label(
                        label=app.display_name or "Unknown",
                        v_align="center",
                        h_align="center",
                    ),
                ],
            ),
            tooltip_text=app.description,
            on_clicked=_on_clicked,
            **kwargs,
        )

    def launch_by_order(self, order: int = 0) -> bool:
        if not self._last_filtered:
            return False
        if order < 0 or order >= len(self._last_filtered):
            return False

        app = self._last_filtered[order]
        try:
            app.launch()
            if getattr(self, "application", None):
                try:
                    self.application.quit()
                except Exception:
                    pass
            else:
                launcher = self._find_launcher_in_parents()
                if launcher is not None:
                    try:
                        launcher.tools.close()
                    except Exception:
                        try:
                            launcher.tools.force_close()
                        except Exception:
                            pass
        except Exception:
            return False
        return True
