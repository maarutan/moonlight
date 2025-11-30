from typing import Iterable, Protocol
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.eventbox import EventBox


class Stylable(Protocol):
    """Protocol for stylable widgets."""

    def add_style_class(self, name: str | Iterable[str]): ...
    def remove_style_class(self, name: str | Iterable[str]): ...
    def is_visible(self) -> bool: ...
    def show(self): ...
    def hide(self): ...


class BaseWidget:
    """Mixin providing toggle() and set_has_class() helpers."""

    def toggle(self: Stylable):
        if self.is_visible():
            self.hide()
        else:
            self.show()

    def set_has_class(self: Stylable, class_name: str | Iterable[str], condition: bool):
        if condition:
            self.add_style_class(class_name)
        else:
            self.remove_style_class(class_name)


class BoxWidget(Box, BaseWidget):
    def __init__(self, spacing=None, style_classes=None, **kwargs):
        all_styles = ["panel-box"]
        if style_classes:
            all_styles.extend(
                [style_classes] if isinstance(style_classes, str) else style_classes
            )
        super().__init__(spacing=spacing or 4, style_classes=all_styles, **kwargs)


class EventBoxWidget(EventBox, BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(style_classes="panel-eventbox", **kwargs)
        self.box = Box(style_classes="panel-box")
        self.add(self.box)


class ButtonWidget(Button, BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(style_classes="panel-button", **kwargs)
        self.box = Box()
        self.add(self.box)
