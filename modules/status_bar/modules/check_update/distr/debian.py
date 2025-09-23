from .abc_dist import *


class Debian(PackageManager):
    def __init__(self):
        self.name = "debian"
        self.pkg_manager = "apt"
        self.icon = ""

    def quantity(self) -> int:
        if not which("apt"):
            return 0
        try:
            result = subprocess.check_output(
                "apt list --upgradeable 2>/dev/null | grep -v Listing | wc -l",
                shell=True,
                text=True,
            ).strip()
            return int(result) if result.isdigit() else 0
        except subprocess.CalledProcessError:
            return 0
