import shlex
import re
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.utils import exec_shell_command
from gi.repository import GLib, Gdk  # type: ignore
from config import STATUS_BAR_LOCK_MODULES
from utils import JsonManager


class Memory(Box):
    def __init__(
        self,
        interval: int = 2,
        format: str = "used/total",
        orientation_pos: bool = True,
        icon: str = "",
    ):
        self.interval = interval
        self.format = format
        self.icon = icon
        self.orientation_pos = orientation_pos
        self.json = JsonManager()

        self._label = Label(name="memory-label", text="–")

        self.button = Button(
            name="memory-button",
            child=self._label,
            on_clicked=self.do_clicked,
        )

        super().__init__(
            name="memory",
            orientation="h" if self.orientation_pos else "v",
            children=self.button,
        )

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self._on_box_click)

        # Создаём файлик состояния
        STATUS_BAR_LOCK_MODULES.parent.mkdir(parents=True, exist_ok=True)
        STATUS_BAR_LOCK_MODULES.touch(exist_ok=True)

        self.update_memory()
        GLib.timeout_add_seconds(self.interval, self.update_memory_timer)

    def _on_box_click(self, widget, event):
        self.button.emit("clicked")
        return True

    def do_clicked(self, *args):
        print("[Memory] Clicked via subclass!")

    def update_memory_timer(self) -> bool:
        self.update_memory()
        return True

    def parse_size(self, value: str) -> float:
        size_match = re.match(r"([\d.]+)([KMGTP]?i?)", value)
        if not size_match:
            return 0.0

        num, unit = size_match.groups()
        num = float(num)
        unit = unit.upper()

        units = {
            "": 1 / (1024**3),
            "K": 1 / (1024**2),
            "M": 1 / 1024,
            "G": 1,
            "T": 1024,
            "P": 1024**2,
            "KI": 1 / (1024**2),
            "MI": 1 / 1024,
            "GI": 1,
            "TI": 1024,
            "PI": 1024**2,
        }

        return round(num * units.get(unit, 1), 2)

    def update_memory(self):
        try:
            out = exec_shell_command("free -h")
            line = next(l for l in out.splitlines() if l.startswith("Mem:"))  # type: ignore
            parts = shlex.split(line)

            total = self.parse_size(parts[1])
            used = self.parse_size(parts[2])
            free = self.parse_size(parts[3])

            if self.format == "used":
                text = (
                    f"{self.icon} {used:.1f} GB"
                    if self.orientation_pos
                    else f"{self.icon}\n{used:.1f}"
                )

            elif self.format == "free":
                text = (
                    f"{self.icon} {free:.1f} GB"
                    if self.orientation_pos
                    else f"{self.icon}\n{free:.1f}"
                )

            elif self.format == "used/total":
                text = (
                    f"{self.icon} {used:.1f}/{total:.1f}"
                    if self.orientation_pos
                    else f"{self.icon}\n{used:.1f}\n{total:.1f}"
                )

            elif self.format == "total/used":
                text = (
                    f"{self.icon} {total:.1f}/{used:.1f}"
                    if self.orientation_pos
                    else f"{self.icon}\n{total:.1f}\n{used:.1f}"
                )

            else:  # fallback
                text = (
                    f"{self.icon} {used:.1f}/{free:.1f}"
                    if self.orientation_pos
                    else f"{self.icon}\n{used:.1f}\n{free:.1f}"
                )

            self._label.set_text(text)

            self.json.update(
                path=STATUS_BAR_LOCK_MODULES,
                key="memory.used",
                new_value=used,
            )
            self.json.update(
                path=STATUS_BAR_LOCK_MODULES,
                key="memory.free",
                new_value=free,
            )

        except Exception as e:
            self._label.set_text("err")
            print(f"[Memory] Error: {e}")
