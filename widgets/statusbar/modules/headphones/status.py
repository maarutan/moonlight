from typing import TYPE_CHECKING, Optional
from fabric.utils import exec_shell_command_async
from utils.constants import Const
import shlex

if TYPE_CHECKING:
    from .headphone_widget import HeadphoneWidget


class HeadphoneStatus:
    def __init__(self, headphone: "HeadphoneWidget"):
        self.headphone = headphone
        self.status = ""
        self.percent = 0
        self.name = "unknown"
        self.title = "Headphones"
        self.body: Optional[str] = None
        self.timeout = self.headphone.statusbar.confh.config_modules["headphones"][
            "notify-timeout"
        ]
        self.update()

    def update(self):
        self.status = getattr(self.headphone.provider, "status", "unknown")
        try:
            self.percent = int(self.headphone.headset.first_percentage() or 0)
        except Exception:
            self.percent = 0
        headsets = getattr(self.headphone.headset, "list_headsets", lambda: {})() or {}
        names = (
            getattr(self.headphone.headset, "list_headset_names", lambda: {})() or {}
        )
        if self.status == "bluetooth" and headsets:
            first_path = next(iter(headsets))
            self.percent = headsets.get(first_path, self.percent)
            self.name = names.get(first_path, first_path)
            self.body = (
                f"Name: {self.name}\nPower: {self.percent:0.0f}%\nStatus:{self.status}"
            )
        else:
            self.name = getattr(
                self.headphone.provider, "default_sink_device_name", "Unknown Device"
            )
            self.body = f"Name: {self.name}\nStatus: {self.status}"

    def send_notify(self):
        self.update()
        if not self.body:
            return
        path = Const.TEMP_DIR / "tmp_headphones.svg"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(getattr(self.headphone.icon_handler, "icon", "") or "")
        except Exception:
            pass
        icon_path = path.as_posix()
        title_quoted = shlex.quote(self.title)
        body_quoted = shlex.quote(self.body)
        icon_quoted = shlex.quote(icon_path)
        app_quoted = shlex.quote(Const.APP_NAME)
        cmd = f"notify-send -t {int(self.timeout)} {title_quoted} {body_quoted} -i {icon_quoted} -a {app_quoted}"
        exec_shell_command_async(cmd)
