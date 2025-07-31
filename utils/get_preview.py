import subprocess
import requests
import tempfile
from shutil import rmtree
from random import randint
from loguru import logger
from pathlib import Path


class GetPreviewPath:
    def __init__(self) -> None:
        self.tmp_path = Path(tempfile.gettempdir()) / "moonlight"
        if self.tmp_path.exists():
            rmtree(self.tmp_path)
        self.tmp_path.mkdir(exist_ok=True, parents=True)

    def validator(self, path: str) -> Path | None:
        try:
            if path.startswith("http://") or path.startswith("https://"):
                return self._get_if_url(path)
            else:
                return self._get_if_local(path)
        except Exception as e:
            logger.error(f"Error getting preview from '{path}': {e}")
            return None

    def _get_if_url(self, url: str) -> Path | None:
        # Используем имя файла из URL или фиксированное, чтобы кэшировать по URL
        filename = url.split("/")[-1]
        if not filename:
            filename = "preview.png"
        path_img = self.tmp_path / filename

        # Если уже есть файл, сразу возвращаем
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

        # Если файл уже скопирован, не копируем снова
        if target.exists():
            return target.resolve()

        try:
            with open(source, "rb") as src, open(target, "wb") as dst:
                dst.write(src.read())
            return target.resolve()
        except Exception as e:
            logger.error(f"Error getting preview from local path '{path}': {e}")
            return None
