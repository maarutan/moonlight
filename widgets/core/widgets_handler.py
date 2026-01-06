import os
from fabric import Application
from utils.constants import Const
from loguru import logger

from ..initialization import WIDGETS
from .config import ConfigHandlerWidgets
from .stylesheet import Stylesheet


class WidgetsHandler:
    def __init__(self) -> None:
        Const.APP_PID_FILE.write_text(str(os.getpid()))
        self.confh = ConfigHandlerWidgets()
        Stylesheet(self)
        modules = [m for m in WIDGETS if m is not None]
        self.windows = self._load_enabled_modules(modules)
        self.app = Application(Const.APP_NAME, *self.windows)

    def _load_enabled_modules(self, modules: list) -> list:
        loaded = []
        for module in modules:
            try:
                instance = module()
                if instance is None:
                    logger.info(
                        f"[{getattr(module, '__name__', str(module))}] returned None (disabled)."
                    )
                    continue
                loaded.append(instance)
            except Exception:
                name = getattr(module, "__name__", repr(module))
                logger.exception(f"[{name}] Failed to initialize")
        return loaded
