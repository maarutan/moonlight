from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.grid import Grid
from utils.widget_utils import setup_cursor_hover

if TYPE_CHECKING:
    from .core import NotifyCore


class ActionButtonsHandler(Box):
    def __init__(self, notify_core: "NotifyCore"):
        self.notify_core = notify_core
        self.notif = self.notify_core._notification
        super().__init__(spacing=4, orientation="v")

        if not self.notif.actions:
            return

        grid = Grid(
            row_spacing=4,
            column_spacing=4,
            column_homogeneous=True,
        )

        buttons = []
        for action in self.notif.actions:
            btn = Button(
                name="notification-action-button",
                h_expand=True,
                v_expand=True,
                label=action.label,
                on_clicked=lambda *_, action=action: action.invoke(),
            )
            setup_cursor_hover(btn)
            buttons.append(btn)

        grid.attach_flow(buttons, columns=2)
        self.add(grid)
