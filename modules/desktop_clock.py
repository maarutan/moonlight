from fabric.widgets.box import Box
from fabric.widgets.datetime import DateTime
from fabric.widgets.wayland import WaylandWindow as Window


class DesktopClock(Window):
    """
    A simple desktop clock widget.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="desktop_clock",
            layer="bottom",
            anchor="center left",
            h_align="start",
            v_align="start",
            child=Box(
                name="desktop-clock-box",
                orientation="v",
                children=[
                    DateTime(
                        h_align="start",
                        v_align="start",
                        formatters=["%I:%M:%S"],
                        name="clock",
                    ),
                    DateTime(
                        h_align="start",
                        v_align="start",
                        formatters=["%m/%d/%y"],
                        interval=3600000,  # Update every hour
                        name="date",
                    ),
                ],
            ),
            all_visible=True,
            **kwargs,
        )
