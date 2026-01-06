from fabric.utils.helpers import Gtk
from typing import Callable, Literal, Optional
from fabric.widgets.box import Box
from fabric.widgets.entry import Entry


class Input(Box):
    def __init__(
        self,
        *,
        name: str | None = None,
        label_text: str = "Value:",
        initial_value: str = "",
        tooltip_text: Optional[str] = None,
        trigger: Literal["submit", "change"] = "submit",
        **kwargs,
    ) -> None:
        super().__init__(spacing=6, orientation="h", **kwargs)

        self._trigger = trigger
        self._external_change_cb: Optional[Callable[[str], None]] = None

        # Label
        self._label = Gtk.Label(label=label_text)
        self._label.set_xalign(0.0)

        # 💥 fabric Entry вместо Gtk.Entry
        self._entry = Entry(
            name=name,
            text=initial_value,
            placeholder="Enter value...",
            editable=True,
            h_expand=False,
        )
        self._entry.style_classes = "Input"

        if tooltip_text:
            self.set_tooltip_text(tooltip_text)

        # Layout
        self.pack_start(self._label, False, False, 0)
        self.pack_start(self._entry, False, False, 0)

        if trigger == "submit":
            self._entry.connect("activate", self._on_entry_submit)
        else:
            self._entry.connect("changed", self._on_entry_changed)

        self.show_all()

    def get_value(self) -> str:
        return self._entry.get_text()

    def set_value(self, value: str) -> None:
        self._entry.set_text(value)

    def set_on_change_callback(self, cb: Callable[[str], None]) -> None:
        self._external_change_cb = cb

    def _on_entry_changed(self, entry: Gtk.Entry) -> None:
        text = entry.get_text()
        if self._external_change_cb:
            self._external_change_cb(text)
        self.on_change(text)

    def _on_entry_submit(self, entry: Gtk.Entry) -> None:
        text = entry.get_text()
        if self._external_change_cb:
            self._external_change_cb(text)
        self.on_submit(text)

    def on_change(self, new_text: str) -> None:
        pass

    def on_submit(self, new_text: str) -> None:
        pass
