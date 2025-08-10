import subprocess
import requests
import tempfile
import hashlib
from shutil import rmtree
from loguru import logger
import time
from pathlib import Path
from config import PLACEHOLDER_IMAGE, APP_NAME
from threading import Thread, Timer


class GetPreviewPath:
    def __init__(self) -> None:
        self.tmp_path = Path(tempfile.gettempdir()) / APP_NAME
        # if self.tmp_path.exists():
        # rmtree(self.tmp_path)
        self.tmp_path.mkdir(exist_ok=True, parents=True)
        self.CLEANUP_INTERVAL = 60 * 60
        self.MAX_FILE_AGE = 60 * 60 * 3

        self.loading_files = set()
        self._start_cleanup_timer()

    def _start_cleanup_timer(self):
        def cleanup():
            now = time.time()
            deleted = 0

            for file in self.tmp_path.iterdir():
                if file.is_file():
                    age = now - file.stat().st_mtime
                    if age > self.MAX_FILE_AGE:
                        try:
                            file.unlink()
                            deleted += 1
                        except Exception as e:
                            logger.warning(f"Failed to delete {file}: {e}")
            if deleted:
                logger.info(f"Cleaned up {deleted} old preview files")
            Timer(self.CLEANUP_INTERVAL, cleanup).start()

        Timer(self.CLEANUP_INTERVAL, cleanup).start()

    def _get_filename_from_url(self, url: str) -> str:
        hash_digest = hashlib.md5(url.encode("utf-8")).hexdigest()
        return f"{hash_digest}.png"

    def validator(self, path: str) -> Path:
        try:
            if path.startswith(("http://", "https://")):
                filename = self._get_filename_from_url(path)
                path_img = self.tmp_path / filename

                if path_img.exists():
                    return path_img.resolve()

                if filename in self.loading_files:
                    return Path(PLACEHOLDER_IMAGE)

                self.loading_files.add(filename)
                Thread(
                    target=self._download_url,
                    args=(path, path_img, filename),
                    daemon=True,
                ).start()

                return Path(PLACEHOLDER_IMAGE)

            elif path == "":
                return Path(PLACEHOLDER_IMAGE)
            else:
                return self._get_if_local(path) or Path(PLACEHOLDER_IMAGE)

        except Exception as e:
            logger.error(f"Error getting preview from '{path}': {e}")
            return Path(PLACEHOLDER_IMAGE)

    def _download_url(self, url: str, path_img: Path, filename: str) -> None:
        try:
            if path_img.exists():
                logger.info(f"Preview already exists, skip download: {path_img}")
                return

            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                with open(path_img, "wb") as f:
                    f.write(response.content)
                logger.info(f"Downloaded preview from {url}")
            else:
                logger.warning(f"Non-200 response ({response.status_code}) for: {url}")
        except Exception as e:
            logger.error(f"Error downloading preview from URL '{url}': {e}")
        finally:
            self.loading_files.discard(filename)

    def _get_if_url(self, url: str) -> Path | None:
        filename = url.split("/")[-1]
        if not filename:
            filename = "preview.png"
        path_img = self.tmp_path / filename

        if path_img.exists():
            return path_img.resolve()

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                with open(path_img, "wb") as f:
                    f.write(response.content)
                return path_img.resolve()
            else:
                logger.warning(f"Non-200 response ({response.status_code}) for: {url}")
                return None
        except Exception as e:
            logger.error(f"Error getting preview from URL '{url}': {e}")
            return None

    def _get_if_local(self, path: str) -> Path | None:
        if path.startswith("file://"):
            path = path[7:]

        source = Path(path)
        if not source.exists():
            logger.error(f"Local file not found: {path}")
            return None

        target = self.tmp_path / source.name

        if target.exists():
            return target.resolve()

        try:
            with open(source, "rb") as src, open(target, "wb") as dst:
                dst.write(src.read())
            return target.resolve()
        except Exception as e:
            logger.error(f"Error getting preview from local path '{path}': {e}")
            return None
