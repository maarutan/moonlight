import time
import subprocess
import threading
from fabric.core.service import Service, Property, Signal


class AudioStatusProvider(Service):
    status = Property(type=str, default_value="unknown")
    changed = Signal(name="changed")

    def __init__(self):
        super().__init__()

        self.status = self._get_default_sink_type()

        self._stop = False
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
        )
        self._thread.start()

    def _poll_loop(self):
        while not self._stop:
            new_status = self._get_default_sink_type()
            self.update_status(new_status)
            time.sleep(1)

    def update_status(self, new_status: str):
        if not new_status:
            new_status = "unknown"

        if new_status == self.status:
            return

        self.status = new_status
        self.emit("changed")

    def _get_default_sink_type(self) -> str:
        default = self._get_default_sink_name()
        if not default:
            return "unknown"
        sinks = self._parse_pactl_sinks()
        data = sinks.get(default)
        if not data:
            return "unknown"
        return self._detect_sink_type_from_props(default, data)

    def _parse_pactl_sinks(self) -> dict:
        out = self.run_cmd(["pactl", "list", "sinks"])
        sinks = {}
        cur = None
        props = {}
        active_port = ""
        in_props = False
        for line in out.splitlines():
            stripped = line.strip()
            if stripped.startswith("Name:"):
                if cur:
                    sinks[cur] = {"active_port": active_port or "", "props": props}
                cur = stripped.split(":", 1)[1].strip()
                props = {}
                active_port = ""
                in_props = False
                continue
            if cur is None:
                continue
            if stripped.startswith("Active Port:"):
                active_port = stripped.split(":", 1)[1].strip()
                continue
            if stripped.startswith("Properties:"):
                in_props = True
                continue
            if in_props and line.startswith("\t") and "=" in line:
                left, right = line.strip().split("=", 1)
                props[left.strip()] = right.strip().strip('"')
        if cur:
            sinks[cur] = {"active_port": active_port or "", "props": props}
        return sinks

    def _get_default_sink_name(self) -> str | None:
        out = self.run_cmd(["pactl", "info"])
        for line in out.splitlines():
            if line.startswith("Default Sink:"):
                return line.split(":", 1)[1].strip()

        return None

    def _detect_sink_type_from_props(self, sink_name: str, sink_data: dict) -> str:
        props = sink_data.get("props", {})
        node = props.get("node.name", "").lower()
        desc = props.get("device.description", "").lower()
        bus = props.get("device.bus", "").lower()
        if bus == "usb" or node.startswith("alsa_output.usb"):
            return "usb"
        if "bluez" in node or "bluetooth" in desc:
            return "bluetooth"
        if "hdmi" in node or "displayport" in desc:
            return "hdmi"
        port = (sink_data.get("active_port") or "").lower()
        if "headphone" in port or "headset" in port:
            return "aux"
        return "unknown"

    def run_cmd(self, cmd: list) -> str:
        try:
            return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        except Exception:
            return ""

    @property
    def default_sink_device_name(self) -> str:
        default = self._get_default_sink_name()
        sinks = self._parse_pactl_sinks()
        data = sinks.get(default, {})
        return data.get("props", {}).get("device.description", default or "unknown")
