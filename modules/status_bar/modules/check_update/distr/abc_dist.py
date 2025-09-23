from abc import ABC, abstractmethod
import subprocess
from shutil import which


class PackageManager(ABC):
    name: str
    pkg_manager: str
    icon: str

    @abstractmethod
    def quantity(self) -> int: ...
