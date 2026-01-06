import subprocess
import json
from fabric.core.service import Service, Property, Signal


def run_cmd(cmd: list) -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def get_default_sink_name() -> str | None:
    out = run_cmd(["pactl", "info"])
    for line in out.splitlines():
        if line.startswith("Default Sink:"):
            return line.split(":", 1)[1].strip()
    return None


def parse_pactl_sinks() -> dict:
    out = run_cmd(["pactl", "list", "sinks"])
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


def detect_sink_type_from_props(sink_name: str, sink_data: dict) -> str:
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


def get_default_sink_type() -> str:
    default = get_default_sink_name()
    if not default:
        return "unknown"
    sinks = parse_pactl_sinks()
    data = sinks.get(default)
    if not data:
        return "unknown"
    return detect_sink_type_from_props(default, data)


class AudioStatusProvider(Service):
    # тип и дефолт свойства
    status = Property(type=str, default_value="unknown")
    # сигнал "changed"
    changed = Signal(name="changed")

    def __init__(self):
        super().__init__()
        # текущий тип аудио
        self.status = get_default_sink_type()

    def update_status(self, new_status: str):
        """
        Эмитим сигнал только если тип аудио реально поменялся:
        aux, bluetooth, usb, hdmi и т.д.
        """
        if new_status is None:
            new_status = "unknown"

        if new_status == self.status:
            return  # тип не поменялся — сигнал не идёт

        self.status = new_status
        self.emit("changed")  # уведомляем слушателей

    def get_status_json(self) -> str:
        return json.dumps({"type": self.status})
