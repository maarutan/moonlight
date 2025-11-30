import fabric
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore
from fabric.widgets.box import Box


class FilePicker(Box):
    def __init__(
        self,
        title: str = "Select file",
        on_select=None,
        on_open=None,
        on_close=None,
        **kwargs,
    ):
        super().__init__(**kwargs, orientation="v", spacing=8)

        self.title = title
        self.on_select = on_select
        self.on_open = on_open
        self.on_close = on_close

        # ─── UI Elements ───────────────────────────────
        self.button = Gtk.Button(label="📁 Open File")
        self.button.set_name("ml-filepicker-button")

        self.pack_start(self.button, False, False, 0)

        self.button.connect("clicked", self._on_button_clicked)

    # ────────────────────────────────────────────────
    def _on_button_clicked(self, _):
        dialog = Gtk.FileChooserDialog(
            title=self.title,
            parent=self._get_valid_parent(),  # type: ignore
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.set_name("ml-filepicker-dialog")

        dialog.add_buttons(
            Gtk.STOCK_CANCEL,  # type: ignore
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,  # type: ignore
            Gtk.ResponseType.OK,
        )

        filter_img = Gtk.FileFilter()
        filter_img.set_name("Image files")
        for mime in ["image/png", "image/jpeg", "image/webp"]:
            filter_img.add_mime_type(mime)
        for ext in ["*.jpg", "*.jpeg", "*.png"]:
            filter_img.add_pattern(ext)
        dialog.add_filter(filter_img)

        if callable(self.on_open):
            self.on_open(dialog)

        dialog.connect("response", self._on_response)
        dialog.connect("destroy", self._on_destroy)
        dialog.show_all()  # type: ignore
        self.dialog = dialog

    # ────────────────────────────────────────────────
    def _get_valid_parent(self):
        parent = self.get_toplevel()
        if parent and getattr(parent, "get_visible", lambda: False)():
            return parent
        return None

    # ────────────────────────────────────────────────
    def _on_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if callable(self.on_select):
                self.on_select(filename)
        dialog.destroy()

    # ────────────────────────────────────────────────
    def _on_destroy(self, dialog):
        if callable(self.on_close):
            self.on_close(dialog)
