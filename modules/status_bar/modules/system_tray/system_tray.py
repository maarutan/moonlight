from .tray_items import TrayItems
from .tray_button_handler import TrayButtonHandler

from fabric.widgets.box import Box


class SystemTrayHandler(Box):
    def __init__(
        self,
        bar_position: str,
        tray_box_position: str,
        spacing: int = 8,
        tray_box: bool = True,
        pixel_size: int = 20,
        refresh_interval: int = 1,
        orientation_pos: bool = True,
    ):
        self.spacing = spacing
        self.tray_box = tray_box
        self.pixel_size = pixel_size
        self.bar_position = bar_position
        self.orientation_pos = orientation_pos
        self.refresh_interval = refresh_interval
        self.tray_box_position = tray_box_position

        super().__init__(
            name="statusbar-systemtray-container",
            children=self._make_content(),
            orientation="h" if orientation_pos else "v",
        )

    def _make_content(self) -> TrayButtonHandler | TrayItems:
        if self.tray_box:
            return TrayButtonHandler(
                bar_position=self.bar_position,
                orientation_pos=self.orientation_pos,
                tray_box_position=self.tray_box_position,
            )

        else:
            return TrayItems(
                grid=self.tray_box,
                spacing=self.spacing,
                pixel_size=self.pixel_size,
                orientation_pos=self.orientation_pos,
                refresh_interval=self.refresh_interval,
            )
