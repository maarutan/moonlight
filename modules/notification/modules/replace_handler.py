from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import NotifyCore


class ReplaceHandler:
    def __init__(
        self,
        class_init: "NotifyCore",
        active_widgets_by_replace_id: dict[int, "NotifyCore"],
    ):
        self.conf = class_init
        self.notif = self.conf._notification
        self.active_widgets_by_replace_id = active_widgets_by_replace_id
        self._handle_replace()

    def _handle_replace(self):
        replaces_id = getattr(self.notif, "replaces_id", 0) or 0
        nid = getattr(self.notif, "id", None)

        if replaces_id and replaces_id in self.active_widgets_by_replace_id:
            existing_widget = self.active_widgets_by_replace_id[replaces_id]
            if parent := existing_widget.get_parent():
                parent.remove(existing_widget)  # type: ignore
            try:
                existing_widget.destroy()
            except Exception:
                pass
            self.active_widgets_by_replace_id.pop(replaces_id, None)

        if replaces_id:
            self.active_widgets_by_replace_id[replaces_id] = self.conf
        elif nid is not None:
            self.active_widgets_by_replace_id[nid] = self.conf
