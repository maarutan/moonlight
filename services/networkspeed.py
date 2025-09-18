import re

from fabric.utils import exec_shell_command


class NetworkSpeed:
    """A service to monitor network speed."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkSpeed, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.interval = 1000
        self.last_total_down_bytes = 0
        self.last_total_up_bytes = 0

    def get_network_speed(self):
        lines = exec_shell_command("cat /proc/net/dev").split("\n")  # pyright: ignore[reportAttributeAccessIssue]]
        total_down_bytes = 0
        total_up_bytes = 0

        for line in lines:
            fields = re.split(r"\W+", line.strip())
            if len(fields) <= 2:
                continue

            interface = fields[0]
            try:
                current_interface_down_bytes = int(fields[1])
                current_interface_up_bytes = int(fields[9])
            except ValueError:
                continue

            # Skip virtual interfaces or interfaces with invalid byte counts
            if (
                interface == "lo"
                or re.match(r"^ifb[0-9]+", interface)
                or re.match(r"^lxdbr[0-9]+", interface)
                or re.match(r"^virbr[0-9]+", interface)
                or re.match(r"^br[0-9]+", interface)
                or re.match(r"^vnet[0-9]+", interface)
                or re.match(r"^tun[0-9]+", interface)
                or re.match(r"^tap[0-9]+", interface)
                or current_interface_down_bytes < 0
                or current_interface_up_bytes < 0
            ):
                continue

            total_down_bytes += current_interface_down_bytes
            total_up_bytes += current_interface_up_bytes

        # Compute the speeds
        if self.last_total_down_bytes == 0:
            self.last_total_down_bytes = total_down_bytes
        if self.last_total_up_bytes == 0:
            self.last_total_up_bytes = total_up_bytes

        download_speed = (total_down_bytes - self.last_total_down_bytes) / self.interval
        upload_speed = (total_up_bytes - self.last_total_up_bytes) / self.interval

        self.last_total_down_bytes = total_down_bytes
        self.last_total_up_bytes = total_up_bytes

        return {"download": download_speed, "upload": upload_speed}


if __name__ == "__main__":
    sp = NetworkSpeed()

    print(sp.get_network_speed())
