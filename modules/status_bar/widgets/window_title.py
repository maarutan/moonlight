from typing import TYPE_CHECKING, Optional
from types import SimpleNamespace

from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.hyprland.service import Hyprland, HyprlandEvent
from fabric.utils.helpers import idle_add

from shared.app_icon import AppIcon
from shared.app_name_relover import AppNameResolver
from utils.constants import Const
from utils.widget_utils import merge

if TYPE_CHECKING:
    from ..bar import StatusBar


class WindowTitleWidget(Box):
    def __init__(self, init_class: "StatusBar"):
        self.conf = init_class
        super().__init__(
            name="sb_window-title",
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
        )

        config = self.conf.confh.get_option(
            f"{self.conf.widget_name}.widgets.window-title", {}
        )

        if not self.conf.is_horizontal():
            config = merge(config, config.get("if-vertical", {}))

        self.conf_type: str = config.get("type", "class")
        self.conf_vertical_length: int = int(
            config.get(
                "vertical-length", config.get("icon", {}).get("vertical-length", 3) or 3
            )
        )
        self.conf_title_length: int = int(config.get("title-length", 20) or 20)

        self.conf_unknown_title: str = str(config.get("unknown-title", "Unknown"))
        self.conf_icon = config.get("icon", {}) or {}
        self.conf_icon_enabled: bool = bool(self.conf_icon.get("enabled", True))
        self.conf_icon_size: int = int(self.conf_icon.get("size", 32) or 32)
        self.conf_icon_position: str = str(
            self.conf_icon.get("position", "left")
        ).lower()

        self.children = self.create_title(
            window_class="",
            window_title="",
            size=self.conf_icon_size,
        )

        def on_active_window(_, event: HyprlandEvent):
            raw_class = event.data[0]
            raw_title = event.data[1]

            win_class = str(raw_class or "")
            win_title = str(raw_title or "")

            self.children = self.create_title(
                window_class=win_class,
                window_title=win_title,
                size=self.conf_icon_size,
            )

        self.hypr = Hyprland()
        self.hypr.connect("event::activewindow", callback=on_active_window)

        dummy_event = SimpleNamespace(data=["", ""])
        idle_add(lambda: on_active_window(None, dummy_event))

        self.show_all()

    def create_title(
        self,
        window_class: str,
        window_title: str,
        size: int,
    ) -> Box:
        window_class = (window_class or "").strip() or self.conf_unknown_title
        resolved_name = AppNameResolver.resolve_name(window_class)
        display_text = resolved_name

        window_title = (window_title or "").strip() or self.conf_unknown_title

        is_horizontal = self.conf.is_horizontal()
        if not is_horizontal:
            if len(display_text) > self.conf_vertical_length:
                text = display_text[: self.conf_vertical_length] + "…"
            else:
                text = display_text
        else:
            if self.conf_type == "class":
                text = display_text[: self.conf_title_length]
            else:
                if len(window_title) > self.conf_title_length:
                    text = window_title[: self.conf_title_length] + " …"
                else:
                    text = window_title

        icon_widget: Optional[Box] = None
        if self.conf_icon_enabled:
            if window_class == self.conf_unknown_title:
                icon_widget = Image(
                    image_file=Const.PLACEHOLDER_IMAGE_GHOST.as_posix(),
                    size=size,
                )
            else:
                try:
                    icon_widget = AppIcon(
                        app_name=resolved_name,
                        include_hidden=True,
                        icon_size=size,
                    )
                except Exception:
                    icon_widget = Image(
                        image_file=Const.PLACEHOLDER_IMAGE_GHOST.as_posix(), size=size
                    )

        if not is_horizontal:
            stack_box = Box(
                name="sb_window-title-box-vertical",
                h_expand=True,
                v_expand=True,
                h_align="center",
                v_align="center",
                orientation="vertical",
            )

            title_label = Label(label=text, name="sb_window-title-title")

            stack_children = []
            if icon_widget:
                stack_children.append(icon_widget)
            stack_children.append(title_label)

            stack_box.children = stack_children
            return stack_box

        main_box = Box(
            name="sb_window-title-box",
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
            orientation="horizontal",
        )

        title_label = Label(label=text, name="sb_window-title-title")

        if self.conf_icon_position == "left":
            children = []
            if icon_widget:
                children.append(icon_widget)
                children.append(Label(" "))
            children.append(title_label)
        elif self.conf_icon_position == "right":
            children = [title_label]
            children.append(Label(" "))
            if icon_widget:
                children.append(icon_widget)
        else:
            children = []
            if icon_widget:
                children.append(icon_widget)
            children.append(title_label)

        main_box.children = children
        return main_box
