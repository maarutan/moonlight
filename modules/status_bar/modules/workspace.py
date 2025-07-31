from fabric.hyprland.widgets import WorkspaceButton, ActiveWindow
from fabric.hyprland.widgets import Workspaces as HWorkspaces
from fabric.utils import exec_shell_command_async
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from loguru import logger


class Workspaces(Box):
    def __init__(
        self,
        workspaces_numbering=None,
        maximum_value: int = 10,
        orientation_pos: bool = True,
        magic_icon: str = "✨",
        enable_magic: bool = False,
        enable_buttons_factory: bool = True,
    ):
        if workspaces_numbering is None:
            workspaces_numbering = []

        super().__init__(
            name="workspaces-container",
            orientation="h" if orientation_pos else "v",
        )

        def get_label(i):
            base_label = (
                (
                    workspaces_numbering[i - 1]
                    if i - 1 < len(workspaces_numbering)
                    else str(i)
                )
                if workspaces_numbering
                else str(i)
            )
            if i < 0:
                return magic_icon
            return base_label

        workspaces = HWorkspaces(
            name="workspaces",
            invert_scroll=True,
            empty_scroll=True,
            v_align="fill",
            orientation="h" if orientation_pos else "v",
            spacing=0,
            buttons=[
                WorkspaceButton(
                    h_expand=False,
                    v_expand=False,
                    h_align="center",
                    v_align="center",
                    id=i,
                    label=None,
                    style_classes=["buttons-workspace"],
                )
                for i in range(1, maximum_value + 1)
            ],
        )

        max_active = ActiveWindow() if callable(ActiveWindow) else maximum_value
        if not isinstance(max_active, int) or max_active <= 0:
            max_active = maximum_value

        def custom_buttons_factory(i: int):
            if i < 0 and enable_magic:
                return WorkspaceButton(
                    id=i,
                    label=magic_icon,
                    style_classes=["magic-workspace"],
                )
            elif i >= 1 and enable_buttons_factory:
                return WorkspaceButton(
                    id=i,
                    label=str(i),
                    # style_classes=["buttons-workspace"],
                )
            return None

        buttons = [
            WorkspaceButton(
                id=i,
                label=get_label(i),
                # style_classes=["buttons-workspace"],
            )
            for i in range(1, maximum_value + 1)
        ]

        workspaces_num = HWorkspaces(
            name="workspaces-num",
            invert_scroll=True,
            empty_scroll=True,
            v_align="fill",
            orientation="h" if orientation_pos else "v",
            spacing=0,
            buttons=buttons,
            buttons_factory=custom_buttons_factory,
        )
        self.children = [workspaces_num if workspaces_numbering else workspaces]
