import shlex
from fabric.utils.helpers import exec_shell_command_async, GLib
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from typing import TYPE_CHECKING
from utils.widget_utils import setup_cursor_hover

if TYPE_CHECKING:
    from ..bar import StatusBar


class CustomWidget(Box):
    def __init__(self, init_class: "StatusBar", widget_name: str):
        self.cfg = init_class
        self.widget_name = self.cfg.widget_name
        self.confh = self.cfg.confh
        self.custom_name = widget_name

        super().__init__(
            orientation="h" if self.cfg.is_horizontal() else "v",
            spacing=6,
            name=f"custom-{widget_name}",
        )

        base_cfg = self.confh.get_option(
            f"{self.widget_name}.widgets.custom.{widget_name}", {}
        )
        if not self.cfg.is_horizontal() and "if-vertical" in base_cfg:
            cfg = {**base_cfg, **base_cfg["if-vertical"]}
        else:
            cfg = base_cfg

        cmd = cfg.get("cmd", "") or ""
        try:
            interval = int(cfg.get("interval", 0) or 0)
        except Exception:
            interval = 0

        format_str = cfg.get("format", "{}")
        on_clicked = cfg.get("on-clicked")
        w_type = cfg.get("type", "label")

        has_placeholder = "{}" in str(format_str)

        value_label = Label(
            name=f"custom-{widget_name}-label",
            style_classes="status-bar-custom-label",
            label="",
        )

        orientation = "h" if self.cfg.is_horizontal() else "v"

        if orientation == "h":
            value_label.add_style_class(f"status-bar-custom-label-horizontal")
        else:
            value_label.add_style_class(f"status-bar-custom-label-vertical")

        if w_type == "button":
            inner = Box(
                orientation=orientation,
                spacing=6,
                name=f"custom-{widget_name}-inner",
            )
            inner.pack_start(value_label, False, False, 0)
            if on_clicked:
                container = Button(
                    name=f"custom-{widget_name}-button",
                    style_classes="status-bar-custom-button",
                    child=inner,
                    on_clicked=lambda *_: exec_shell_command_async(
                        f"/bin/sh -c {shlex.quote(on_clicked)}"
                    ),
                )
            else:
                container = Button(
                    name=f"custom-{widget_name}-button",
                    style_classes="status-bar-custom-button",
                    child=inner,
                )

            if orientation == "h":
                container.add_style_class(f".status-bar-custom-button-horizontal")
            else:
                container.add_style_class(f".status-bar-custom-button-vertical")

            setup_cursor_hover(container)
        else:
            container = Box(
                orientation=orientation,
                spacing=6,
                name=f"custom-{widget_name}-box",
            )
            container.pack_start(value_label, False, False, 0)
            setup_cursor_hover(container)

        self.pack_start(container, False, False, 0)

        def update_label():
            if not has_placeholder:
                value_label.set_label(str(format_str))
                return False
            if cmd:
                shell_cmd = f"/bin/sh -c {shlex.quote(cmd)}"

                def on_done(output):
                    if output is False:
                        value_label.set_label("ERR")
                    else:
                        value_label.set_label(format_str.format(str(output).strip()))

                exec_shell_command_async(shell_cmd, callback=on_done)
            else:
                value_label.set_label("")
            return True

        update_label()

        if has_placeholder and cmd and interval > 0:
            GLib.timeout_add_seconds(interval, update_label)

        self.show_all()
