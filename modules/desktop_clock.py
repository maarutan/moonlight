from fabric.widgets.box import Box
from fabric.widgets.datetime import DateTime
from fabric.widgets.wayland import WaylandWindow as Window


class DesktopClock(Window):
    """
    A simple desktop clock widget.
    """

    def __init__(
        self,
        enabled: bool = True,
        first_fromat: str = "%I:%M %p",
        second_format: str = "%A, %d %B %Y",
        anchor: str = "top left",
        layer: str = "bottom",
    ):
        super().__init__(
            name="desktop_clock",
            layer=layer,
            anchor=anchor,
            h_align="start",
            v_align="start",
            child=Box(
                name="desktop-clock-box",
                orientation="v",
                children=[
                    DateTime(
                        name="desktop-clock-box-first",
                        h_align="start",
                        v_align="start",
                        formatters=first_fromat,
                    ),
                    DateTime(
                        name="desktop-clock-box-second",
                        h_align="start",
                        v_align="start",
                        formatters=second_format,
                        interval=3600000,  # Update every hour
                    ),
                ],
            ),
        )
        if not enabled:
            self.hide()
