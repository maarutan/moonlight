from pathlib import Path
from shutil import rmtree


class FileManager:
    """File Manager"""

    def __init__(self) -> None:
        """initial path"""

    def is_exists(self, path: Path) -> bool:
        """check if path exists"""
        try:
            return Path(path).exists()
        except Exception as e:
            print(f"Error FileMnager (is_exists): {e}")
            return False

    def delete(self, path: Path) -> None:
        """delete file or directory"""
        try:
            if not self.is_exists(path):
                return

            if path.is_file():
                path.unlink()
            else:
                rmtree(path)

        except Exception as e:
            print(f"Error FileMnager (delete): {e}")

    def append(self, path: Path, content: str) -> None:
        """append content in file"""
        try:
            with open(path, "a") as f:
                f.write(content)
        except Exception as e:
            print(f"Error FileMnager (append): {e}")

    def if_not_exists_create(self, path: Path) -> None:
        try:
            if path.suffix:
                if not path.exists():
                    path.touch()
                    path.parent.mkdir(parents=True, exist_ok=True)
            else:
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error in FileManager (if_not_exists_create): {e}")

    def write(self, path: Path, content: str) -> None:
        try:
            with open(path, "w") as f:
                f.write(content)
        except Exception as e:
            print(f"Error FileMnager (write): {e}")

    def read(self, path: Path):
        if not path.exists():
            return ""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error FileManager (read): {e}")
            return ""
