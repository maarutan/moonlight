from typing import Iterable, Callable
from fabric.core.service import Property
from fabric.widgets.widget import Widget
from fabric.utils.helpers import Gtk
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.eventbox import EventBox
from shared.combotext import ComboText
from fabric.widgets.centerbox import CenterBox
from utils.widget_utils import setup_cursor_hover


class ModuleSelector(Box):  # type: ignore
    @Property(list, "read-write")
    def modules(self) -> list[str]:  # type: ignore
        return getattr(self, "_modules", [])

    @modules.setter
    def modules(self, value: list[str]):
        self._modules = list(value or [])
        self._rebuild_stack()

    def __init__(
        self,
        available: Iterable[str],
        modules: Iterable[str] = (),
        name: str | None = None,
        title: str | None = None,
        **kwargs,
    ):
        Box.__init__(self, orientation="v", spacing=6)
        Widget.__init__(self, name, **kwargs)

        self.placeholder = "[Select module]"
        self.available = list(available)
        self._modules = list(modules)
        self._change_handlers: list[Callable[[list[str]], None]] = []

        frame = Gtk.Frame()
        frame.set_label(title or (name or ""))
        frame.set_label_align(0.0, 0.5)  # type: ignore

        inner = Box(orientation="v", spacing=6)
        inner.set_margin_top(10)
        inner.set_margin_bottom(10)
        inner.set_margin_start(22)
        inner.set_margin_end(22)

        frame.add(inner)  # type: ignore
        self.pack_start(EventBox(child=frame), True, True, 0)

        top = Box(orientation="h", spacing=4)
        inner.pack_start(top, False, False, 0)

        self.combo = ComboText(
            items=[self.placeholder, *self.available],
            active=0,
            h_align="fill",
            h_expand=True,
        )
        top.pack_start(EventBox(child=self.combo), True, True, 0)

        add_btn = Button(name="module-select-add-btn", label="+")
        add_btn.connect("clicked", self._on_add_clicked)
        setup_cursor_hover(add_btn)
        top.pack_start(EventBox(child=add_btn), False, False, 0)

        separator = Box(name="ms_line")
        inner.pack_start(separator, False, True, 0)

        self.stack = Box(orientation="v", spacing=4)
        inner.pack_start(self.stack, True, True, 0)

        self._rebuild_stack()

    def _on_add_clicked(self, *_):
        name = self.combo.value
        if not name or name == self.placeholder or name in self._modules:
            return
        self._modules.append(name)
        self._add_row(name)
        self.combo.value = self.placeholder
        self._emit_changed()

    def _add_row(self, name: str):
        content = Box(name="sm_section-config-close-box", orientation="h", spacing=6)
        content.pack_start(Label(label=name, xalign=0), True, True, 0)
        row_btn = Button(
            name=f"module-select-close-btn",
            child=CenterBox(
                start_children=content,
                end_children=Label(name="module-select-close-label", label="×"),
            ),
            on_clicked=lambda *_: self._remove_module(name, row_btn),
        )

        setup_cursor_hover(row_btn)
        self.stack.pack_start(row_btn, False, False, 0)
        self.stack.show_all()

    def _remove_module(self, name: str, row_btn: Button):
        if name in self._modules:
            self._modules.remove(name)
        self.stack.remove(row_btn)
        self._emit_changed()

    def _rebuild_stack(self):
        for c in list(self.stack.get_children()):
            self.stack.remove(c)
        for name in self._modules:
            self._add_row(name)

    def connect_changed(self, cb: Callable[[list[str]], None]):
        self._change_handlers.append(cb)

    def _emit_changed(self):
        for cb in self._change_handlers:
            cb(self._modules)
