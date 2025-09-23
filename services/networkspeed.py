import re
import time
from utils import FileManager


class NetworkSpeed:
    _instance = None
    fm = FileManager()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkSpeed, cls).__new__(cls)
            cls._instance.interval = 1000  # ms # type: ignore
            cls._instance.last_total_down_bytes = None
            cls._instance.last_total_up_bytes = None
        return cls._instance

    def _format_speed(self, value: float, width: int = 5) -> str:
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        idx = 0
        while value >= 1024 and idx < len(units) - 1:
            value /= 1024.0
            idx += 1
        return f"{value:>{width}.2f} {units[idx]}"

    def get_network_speed(self) -> dict[str, str]:
        raw = self.fm.read("/proc/net/dev")
        lines = raw.split("\n")

        total_down_bytes = 0
        total_up_bytes = 0

        for line in lines:
            fields = re.split(r"\W+", line.strip())
            if len(fields) <= 2:
                continue

            interface = fields[0].rstrip(":")
            try:
                current_interface_down_bytes = int(fields[1])
                current_interface_up_bytes = int(fields[9])
            except ValueError:
                continue

            if (
                interface == "lo"
                or re.match(r"^ifb[0-9]+", interface)
                or re.match(r"^lxdbr[0-9]+", interface)
                or re.match(r"^virbr[0-9]+", interface)
                or re.match(r"^br[0-9]+", interface)
                or re.match(r"^vnet[0-9]+", interface)
                or re.match(r"^tun[0-9]+", interface)
                or re.match(r"^tap[0-9]+", interface)
            ):
                continue

            total_down_bytes += current_interface_down_bytes
            total_up_bytes += current_interface_up_bytes

        interval_sec = self.interval / 1000  # type: ignore

        if self.last_total_down_bytes is None or self.last_total_up_bytes is None:
            self.last_total_down_bytes = total_down_bytes
            self.last_total_up_bytes = total_up_bytes
            return {"download": "0.00 B/s", "upload": "0.00 B/s"}

        delta_down = total_down_bytes - self.last_total_down_bytes
        delta_up = total_up_bytes - self.last_total_up_bytes

        download_speed = delta_down / interval_sec
        upload_speed = delta_up / interval_sec

        self.last_total_down_bytes = total_down_bytes
        self.last_total_up_bytes = total_up_bytes

        return {
            "download": self._format_speed(download_speed),
            "upload": self._format_speed(upload_speed),
        }


if __name__ == "__main__":
    sp = NetworkSpeed()
    while True:
        speed = sp.get_network_speed()
        print(speed)
        time.sleep(1)
