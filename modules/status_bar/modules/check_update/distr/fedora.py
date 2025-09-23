from .abc_dist import *


class Fedora(PackageManager):
    def __init__(self):
        self.name = "fedora"
        self.pkg_manager = "dnf"
        self.icon = ""

    def quantity(self) -> int:
        if not which("dnf"):
            return 0
        try:
            result = subprocess.check_output(
                "dnf list updates -q | tail -n +2 | wc -l",
                shell=True,
                text=True,
            ).strip()
            return int(result) if result.isdigit() else 0
        except subprocess.CalledProcessError:
            return 0
