from fabric import Fabricator, Application
from fabric.utils import exec_shell_command_async, get_relative_path
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window


class CavaWidget(Button):
    """A widget to display the Cava audio visualizer."""

    def __init__(self):
        super().__init__(name="cava")

        cava_command = "cava"
        command = f"kitty --title cava-visualizer sh -c '{cava_command}'"

        color = "#ffffff"
        bars = 10

        cava_label = Label(
            v_align="center",
            h_align="center",
            style=f"color: {color};",
        )

        script_path = get_relative_path("../assets/scripts/cava.sh")

        self.box = Box(spacing=1, children=[cava_label]).build(
            lambda box, _: Fabricator(
                poll_from=f"bash -c '{script_path} {bars}'",
                stream=True,
                on_changed=lambda f, line: cava_label.set_label(line),
            )
        )

        self.connect(
            "clicked", lambda _: exec_shell_command_async(command, lambda *_: None)
        )

        self.add(self.box)


if __name__ == "__main__":
    app = Application("cava")
    win = Window(name="cava-visualizer")
    cava = CavaWidget()

    win.add(cava)
    app.add_window(win)

    app.run()
