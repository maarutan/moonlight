from os import name
from typing import Optional
from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window
from .components.profile_preview import ProfilePreview


class DashboardPopup(Window):
    def __init__(
        self,
        dashboard_profile_preview: dict,
    ):
        super().__init__(
            name="statusbar-profile-dashboard-popup",
            style_classes="statusbar-profile-dashboard-popup",
            layer="top",
            anchor="top left",
            exclusivity="auto",
            h_align="start",
            h_expand=True,
            child=Box(
                children=[
                    ProfilePreview(
                        profile_preview=dashboard_profile_preview,
                    ),
                ]
            ),
        )
