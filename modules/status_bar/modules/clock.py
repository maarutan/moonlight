from fabric.widgets.box import Box
from fabric.widgets.datetime import DateTime


class Clock(Box):
    def __init__(
        self,
        format: int = 242,
        is_horizontal: bool = True,
    ):
        self.format = format
        self.is_horizontal = is_horizontal

        if self.format == 12:
            time_format_horizontal = "%I:%M %p"
            time_format_vertical = "%I\n%M\n%p"
        elif self.format == 24:
            time_format_horizontal = "%H:%M"
            time_format_vertical = "%H\n%M"
        else:
            time_format_horizontal = "%H:%M:%S"
            time_format_vertical = "%H\n%M\n%S"

        self.date_time = DateTime(
            name="statusbar-clock",
            formatters=[time_format_horizontal]
            if self.is_horizontal
            else [time_format_vertical],
            h_align="center" if self.is_horizontal else "fill",
            v_align="center",
            h_expand=True,
            v_expand=True,
            style_classes=["vertical"] if not self.is_horizontal else [],
        )
        super().__init__(
            name="statusbar-clock",
            orientation="h" if self.is_horizontal else "v",
            children=self.date_time,
        )
