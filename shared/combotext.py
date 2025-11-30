from typing import Iterable, Callable
from fabric.core.service import Property
from fabric.widgets.widget import Widget
from fabric.utils.helpers import Gtk, Gdk


class ComboText(Gtk.ComboBoxText, Widget):  # type: ignore
    @Property(str, "read-write", default_value="")
    def value(self) -> str:  # type: ignore
        text = self.get_active_text()
        return text if text is not None else ""

    @value.setter
    def value(self, new_val: str):
        model = self.get_model()
        if model is None:
            return
        for idx, row in enumerate(model):  # type: ignore
            if row[0] == new_val:
                self.set_active(idx)
                break

    @Property(int, "read-write", default_value=0)
    def active_index(self) -> int:  # type: ignore
        return self.get_active()

    @active_index.setter
    def active_index(self, idx: int):
        self.set_active(idx)

    def __init__(
        self,
        items: Iterable[str] = (),
        active: int = 0,
        name: str | None = None,
        visible: bool = True,
        all_visible: bool = False,
        style: str | None = None,
        style_classes: Iterable[str] | str | None = None,
        tooltip_text: str | None = None,
        tooltip_markup: str | None = None,
        h_align: str | Gtk.Align | None = None,
        v_align: str | Gtk.Align | None = None,
        h_expand: bool = False,
        v_expand: bool = False,
        size: Iterable[int] | int | None = None,
        **kwargs,
    ):
        Gtk.ComboBoxText.__init__(self)
        Widget.__init__(
            self,
            name,
            visible,
            all_visible,
            style,
            style_classes,
            tooltip_text,
            tooltip_markup,
            h_align,  # type: ignore
            v_align,  # type: ignore
            h_expand,
            v_expand,
            size,
            **kwargs,
        )

        if h_align is None:
            self.set_halign(Gtk.Align.FILL if h_expand else Gtk.Align.START)
        if v_align is None:
            self.set_valign(Gtk.Align.CENTER)

        self.get_style_context().add_class("combo-text")
        self.set_items(items, active=active)
        self._change_handlers: list[Callable[[str], None]] = []
        self.connect("changed", self._on_changed)

        # ⚙️ добавляем маску событий
        self.add_events(Gdk.EventMask.SCROLL_MASK)
        self.connect("scroll-event", self._on_scroll_event)
        self.connect("button-press-event", self._block_middle_button)

    def _on_scroll_event(self, widget, event):
        # если у виджета есть фокус — просто игнорируем
        if self.is_focus():
            return True
        # иначе пропускаем вверх (чтобы ScrollWindow мог работать)
        return False

    def _block_middle_button(self, widget, event):
        if event.button == 2:
            return True
        return False

    def set_items(self, items: Iterable[str], active: int = 0):
        self.remove_all()
        for text in items:
            self.append_text(text)
        model = self.get_model()
        if model is None:
            self.set_active(-1)
        else:
            n = len(model)
            if n == 0:
                self.set_active(-1)
            else:
                if active < 0 or active >= n:
                    active = 0
                self.set_active(active)

    def connect_changed(self, callback: Callable[[str], None]):
        self._change_handlers.append(callback)

    def _on_changed(self, widget):
        current_text = self.get_active_text() or ""
        for cb in self._change_handlers:
            cb(current_text)
