from fabric.widgets.wayland import WaylandWindow
from fabric.widgets.label import Label
from fabric.widgets.box import Box


class NotchedBar(Box):
    def __init__(
        self, layer="top", position="top", size=40, margin=40, text="󰍜 Бар с выемками"
    ):
        self.layer = layer
        self.position = position
        self.size = size
        self.margin = margin
        self.text = text
        super().__init__(
            children=self.get_all(),
        )

    def create_main_bar(self):
        bar = WaylandWindow(
            name="main-bar",
            anchor=f"{self.position} left right",
            layer=self.layer,
            margin="0px 0px 0px 0px",
            size=self.size,
            exclusivity="normal",
        )
        bar.set_child(
            Box(
                orientation="h",
                spacing=20,
                padding=10,
                children=[
                    Label(self.text, font_size=18),
                ],
            )
        )
        return bar

    def create_left_notch(self):
        anchor = f"{self.position} left"
        notch = WaylandWindow(
            name="left-notch",
            anchor=anchor,
            layer=self.layer,
            margin=f"0px 0px 0px {self.margin}px",
            size=self.size,
            exclusivity="none",
        )
        notch.set_child(Box(children=[Label("(", font_size=26)]))
        return notch

    def create_right_notch(self):
        anchor = f"{self.position} right"
        notch = WaylandWindow(
            name="right-notch",
            anchor=anchor,
            layer=self.layer,
            margin=f"0px {self.margin}px 0px 0px",
            size=self.size,
            exclusivity="none",
        )
        notch.set_child(Box(children=[Label(")", font_size=26)]))
        return notch

    def get_all(self):
        """Возвращает все окна: [бар, левая выемка, правая выемка]"""
        return [
            self.create_main_bar(),
            self.create_left_notch(),
            self.create_right_notch(),
        ]
