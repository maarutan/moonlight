import os
import re
import time
from pathlib import Path


class NetworkSpeedService:
    _instance = None
    H_WIDTH = 11
    V_WIDTH = 4

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.interval = 1000  # pyright: ignore[reportAttributeAccessIssue]
            cls._instance.last_total_down_bytes = None
            cls._instance.last_total_up_bytes = None
        return cls._instance

    def _pad(self, text: str, width: int) -> str:
        if not isinstance(text, str):
            text = str(text)
        if len(text) >= width:
            return text[:width]
        return text.center(width)

    def _format_speed(
        self, value: float, compact: bool = False, ultra_compact: bool = False
    ) -> str:
        try:
            if value is None or value != value:  # NaN check
                value = 0.0
        except Exception:
            value = 0.0

        if value < 0:
            value = 0.0

        if ultra_compact:
            if value >= 1024:
                value /= 1024
            return f"{int(value)}"

        units = ["B/s", "KB/s", "MB/s", "GB/s"] if not compact else ["B", "K", "M", "G"]
        idx = 0
        while value >= 1024 and idx < len(units) - 1:
            value /= 1024.0
            idx += 1

        if compact:
            return f"{int(value)}{units[idx]}"

        formatted = f"{value:.2f} {units[idx]}"
        return self._pad(formatted, self.H_WIDTH)

    def _format_speed_compact_vertical(self, value: float) -> str:
        try:
            if value is None or value != value:
                value = 0.0
        except Exception:
            value = 0.0

        if value < 0:
            value = 0.0

        units = ["B", "K", "M", "G"]
        idx = 0
        while value >= 1024 and idx < len(units) - 1:
            value /= 1024.0
            idx += 1

        if value >= 100:
            display = f"{int(value / 10)}…{units[idx]}"
        else:
            display = f"{int(value)}{units[idx]}"

        return self._pad(display, self.V_WIDTH)

    def get_network_speed(self) -> dict[str, dict[str, str]]:
        try:
            raw = Path("/proc/net/dev").read_text()
        except Exception:
            return {
                "horizontal": {
                    "download": self._pad("0.00 B/s", self.H_WIDTH),
                    "upload": self._pad("0.00 B/s", self.H_WIDTH),
                },
                "vertical": {
                    "download": self._pad("0B", self.V_WIDTH),
                    "upload": self._pad("0B", self.V_WIDTH),
                },
            }

        lines = raw.split("\n")

        total_down_bytes = 0
        total_up_bytes = 0

        for line in lines:
            fields = re.split(r"\W+", line.strip())
            if len(fields) <= 2:
                continue

            interface = fields[0].rstrip(":")
            try:
                current_down = int(fields[1])
                current_up = int(fields[9])
            except (ValueError, IndexError):
                continue

            if interface == "lo" or re.match(
                r"^(ifb|lxdbr|virbr|br|vnet|tun|tap)[0-9]+", interface
            ):
                continue

            total_down_bytes += current_down
            total_up_bytes += current_up

        interval_sec = (self.interval or 1000) / 1000.0  # pyright: ignore[reportAttributeAccessIssue]
        if interval_sec <= 0:
            interval_sec = 1.0

        if self.last_total_down_bytes is None or self.last_total_up_bytes is None:
            self.last_total_down_bytes = total_down_bytes
            self.last_total_up_bytes = total_up_bytes
            return {
                "horizontal": {
                    "download": self._pad("0.00 B/s", self.H_WIDTH),
                    "upload": self._pad("0.00 B/s", self.H_WIDTH),
                },
                "vertical": {
                    "download": self._pad("0B", self.V_WIDTH),
                    "upload": self._pad("0B", self.V_WIDTH),
                },
            }

        delta_down = total_down_bytes - self.last_total_down_bytes
        delta_up = total_up_bytes - self.last_total_up_bytes

        download_speed = max(0.0, delta_down / interval_sec)
        upload_speed = max(0.0, delta_up / interval_sec)

        self.last_total_down_bytes = total_down_bytes
        self.last_total_up_bytes = total_up_bytes

        return {
            "horizontal": {
                "download": self._format_speed(download_speed, compact=False),
                "upload": self._format_speed(upload_speed, compact=False),
            },
            "vertical": {
                "download": self._format_speed_compact_vertical(download_speed),
                "upload": self._format_speed_compact_vertical(upload_speed),
            },
        }


if __name__ == "__main__":
    svc = NetworkSpeedService()
    while True:
        speeds = svc.get_network_speed()
        os.system("clear")
        print("H:", speeds["horizontal"])
        print("V:", speeds["vertical"])
        time.sleep(1)
