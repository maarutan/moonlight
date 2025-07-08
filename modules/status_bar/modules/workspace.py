from fabric.hyprland.widgets import WorkspaceButton, Workspaces
from fabric.utils import exec_shell_command_async
from fabric.widgets.box import Box
from fabric.widgets.label import Label


class WorkspacesBar(Box):
    def __init__(
        self,
        workspaces_numbering=None,
        maximum_value: int = 10,
        orientation_pos: bool = True,
    ):
        if workspaces_numbering is None:
            workspaces_numbering = []

        super().__init__(
            name="workspaces-container",
            orientation="h" if orientation_pos else "v",
        )

        workspaces = Workspaces(
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

        workspaces_num = Workspaces(
            name="workspaces-num",
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
                    label=(
                        workspaces_numbering[i - 1]
                        if i - 1 < len(workspaces_numbering)
                        else str(i)
                    )
                    if workspaces_numbering
                    else str(i),
                )
                for i in range(1, maximum_value + 1)
            ],
        )

        self.children = [workspaces_num if workspaces_numbering else workspaces]
