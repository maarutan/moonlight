from .abc_dist import *


class Arch(PackageManager):
    def __init__(self):
        self.name = "arch"
        self.pkg_manager = "pacman"
        self.icon = "󰮯"

    def quantity(self) -> int:
        if not which("checkupdates"):
            return 0
        try:
            result = subprocess.check_output(
                "checkupdates | wc -l",
                shell=True,
                text=True,
                stderr=subprocess.STDOUT,
            ).strip()
            return int(result) if result.isdigit() else 0
        except subprocess.CalledProcessError:
            return 0
