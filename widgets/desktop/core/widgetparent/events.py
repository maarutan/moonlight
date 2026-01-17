from typing import TYPE_CHECKING
from utils.widget_utils import setup_cursor_hover, set_cursor_now


if TYPE_CHECKING:
    from .parent import DesktopWidget


class WidgetParentEvents:
    def __init__(self, desktopwidget: "DesktopWidget"):
        self.desktopwidget = desktopwidget

        self.desktopwidget.connect("button-press-event", self.on_button_press)
        self.desktopwidget.connect("motion-notify-event", self.on_motion_notify)
        self.desktopwidget.connect("button-release-event", self.on_button_release)

    def on_button_press(self, widget, event):
        if event.button == 1 and self.desktopwidget.desktop.edit_mode:
            self.desktopwidget.dragging = True

            self.desktopwidget.drag_start_root_x = event.x_root
            self.desktopwidget.drag_start_root_y = event.y_root

            alloc = self.desktopwidget.get_allocation()
            self.desktopwidget.widget_start_x = alloc.x
            self.desktopwidget.widget_start_y = alloc.y

            if self.desktopwidget.dragging:
                set_cursor_now(self.desktopwidget, "grab")

        return True

    def on_motion_notify(self, widget, event):
        if not self.desktopwidget.dragging:
            return True

        dx = event.x_root - self.desktopwidget.drag_start_root_x
        dy = event.y_root - self.desktopwidget.drag_start_root_y

        new_x = int(self.desktopwidget.widget_start_x + dx)
        new_y = int(self.desktopwidget.widget_start_y + dy)

        max_x = max(
            0,
            self.desktopwidget.desktop.root.get_allocated_width()
            - self.desktopwidget.get_allocated_width(),
        )
        max_y = max(
            0,
            self.desktopwidget.desktop.root.get_allocated_height()
            - self.desktopwidget.get_allocated_height(),
        )

        new_x = max(0, min(new_x, max_x))
        new_y = max(0, min(new_y, max_y))

        self.desktopwidget.desktop.root.move(self.desktopwidget, new_x, new_y)
        if self.desktopwidget.dragging:
            set_cursor_now(self.desktopwidget, "grab")

        return True

    def on_button_release(self, widget, event):
        if not self.desktopwidget.dragging:
            return True

        self.desktopwidget.dragging = False

        alloc = self.desktopwidget.get_allocation()
        gx, gy = self.desktopwidget.desktop.grid.px_to_cell(alloc.x, alloc.y)
        self.desktopwidget.gx, self.desktopwidget.gy = gx, gy
        x, y = self.desktopwidget.desktop.grid.cell_to_px(gx, gy)
        self.desktopwidget.desktop.root.move(self.desktopwidget, x, y)

        if not self.desktopwidget.dragging:
            set_cursor_now(self.desktopwidget, "arrow")

        return True
