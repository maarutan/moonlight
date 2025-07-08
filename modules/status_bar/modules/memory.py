from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.utils import exec_shell_command
from gi.repository import GLib  # type: ignore
from config import STATUS_BAR_LOCK_MODULES
from utils import JsonManager
import shlex
import re


class Memory(Button):
    def __init__(
        self,
        interval: int = 2,
        fmt: str = "{used:.2f} GB/{free:.2f} GB",
    ):
        self.json = JsonManager()
        self._label = Label(name="memory-label", text="–")
        super().__init__(name="memory", child=self._label)

        self.interval = interval
        self.fmt = fmt

        STATUS_BAR_LOCK_MODULES.parent.mkdir(parents=True, exist_ok=True)
        STATUS_BAR_LOCK_MODULES.touch(exist_ok=True)

        self.update_memory()

        GLib.timeout_add_seconds(self.interval, self.update_memory_timer)

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
            "": 1 / (1024**3),  # байты → ГБ
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
            line = next(l for l in out.splitlines() if l.startswith("Mem:"))  # type:ignore
            parts = shlex.split(line)

            total = self.parse_size(parts[1])
            used = self.parse_size(parts[2])
            free = self.parse_size(parts[3])

            self._label.set_text(self.fmt.format(free=free, used=used))

            current_data = self.json.read(path=STATUS_BAR_LOCK_MODULES) or {}

            if "memory" not in current_data:
                self.json.update(
                    path=STATUS_BAR_LOCK_MODULES,
                    key="memory",
                    new_value={"used": used, "free": free},
                )
            else:
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

    def do_clicked(self, *args):
        print("[Memory] Clicked")
