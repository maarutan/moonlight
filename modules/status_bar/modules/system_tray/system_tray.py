from .tray_items import TrayItems
from .tray_button_handler import TrayButtonHandler

from fabric.widgets.box import Box


class SystemTrayHandler(Box):
    def __init__(
        self,
        tray_box_position: str,
        bar_position: str,
        orientation_pos: bool = True,
        pixel_size: int = 20,
        refresh_interval: int = 1,
        grid: bool = True,
        spacing: int = 8,
    ):
        self.grid = grid
        self.orientation_pos = orientation_pos
        self.tray_box_position = tray_box_position
        self.bar_position = bar_position
        self.pixel_size = pixel_size
        self.refresh_interval = refresh_interval
        self.spacing = spacing

        super().__init__(
            name="systemtray-container",
            orientation="h" if orientation_pos else "v",
            children=self._make_content(),
        )

    def _make_content(self) -> TrayButtonHandler | TrayItems:
        if self.grid:
            return TrayButtonHandler(
                tray_box_position=self.tray_box_position,
                orientation_pos=self.orientation_pos,
                bar_position=self.bar_position,
            )
        else:
            return TrayItems(
                orientation_pos=self.orientation_pos,
                pixel_size=self.pixel_size,
                refresh_interval=self.refresh_interval,
                grid=self.grid,
                spacing=self.spacing,
            )
