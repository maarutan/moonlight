from fabric.hyprland.widgets import WorkspaceButton, ActiveWindow
from fabric.hyprland.widgets import Workspaces as HWorkspaces
from fabric.widgets.box import Box
from loguru import logger


class Workspaces(Box):
    def __init__(
        self,
        numbering_workpieces=None,
        max_visible_workspaces: int = 10,
        is_horizontal: bool = True,
        magic_icon: str = "✨",
        magic_enable: bool = False,
        enable_buttons_factory: bool = True,
    ):
        if numbering_workpieces is None:
            numbering_workpieces = []

        super().__init__(
            name="workspaces-container",
            orientation="h" if is_horizontal else "v",
        )

        def get_label(i):
            base_label = (
                (
                    numbering_workpieces[i - 1]
                    if i - 1 < len(numbering_workpieces)
                    else str(i)
                )
                if numbering_workpieces
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
            orientation="h" if is_horizontal else "v",
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
                for i in range(1, max_visible_workspaces + 1)
            ],
        )

        max_active = (
            ActiveWindow() if callable(ActiveWindow) else max_visible_workspaces
        )
        if not isinstance(max_active, int) or max_active <= 0:
            max_active = max_visible_workspaces

        def custom_buttons_factory(i: int):
            if i < 0 and magic_enable:
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
            for i in range(1, max_visible_workspaces + 1)
        ]

        workspaces_num = HWorkspaces(
            name="workspaces-num",
            invert_scroll=True,
            empty_scroll=True,
            v_align="fill",
            orientation="h" if is_horizontal else "v",
            spacing=0,
            buttons=buttons,
            buttons_factory=custom_buttons_factory,
        )
        self.children = [workspaces_num if numbering_workpieces else workspaces]
