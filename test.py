#!/usr/bin/env python3

import time
import threading
import tracemalloc
import gc
import logging
import sys

from fabric import Application
from fabric.utils import get_relative_path

from modules import (
    ScreenCorners,
    ActivateLinux,
    StatusBar,
)  # NotificationPopup отключён
from config import APP_NAME


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(APP_NAME)


def apply_stylesheet(app: Application) -> None:
    """Загрузить и применить CSS-стили."""
    app.set_stylesheet_from_file(get_relative_path("main.css"))
    logger.debug("Stylesheet applied")


def debug_watchdog(stop_event: threading.Event) -> None:
    """
    Функция для периодического профилирования памяти и подсчёта объектов.
    Запускается в отдельном потоке.
    """
    tracemalloc.start()
    while not stop_event.is_set():
        try:
            time.sleep(10)
            obj_count = len(gc.get_objects())
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")

            logger.debug("Watchdog Tick")
            logger.debug(f"Кол-во Python объектов: {obj_count}")
            logger.debug("Топ-3 по памяти:")
            for stat in top_stats[:3]:
                logger.debug(f"  {stat}")
            logger.debug("-" * 40)
        except Exception as e:
            logger.error(f"Watchdog error: {e}", exc_info=True)


def main() -> None:
    # Инициализация компонентов
    corners = ScreenCorners()
    activate_linux = ActivateLinux()
    bar = StatusBar()

    corners.set_visible(True)

    app = Application(
        APP_NAME,
        corners,
        activate_linux,
        bar,
        # NotificationPopup - отключён
    )

    apply_stylesheet(app)

    stop_event = threading.Event()
    watchdog_thread = threading.Thread(
        target=debug_watchdog, args=(stop_event,), daemon=True
    )
    watchdog_thread.start()

    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Завершение работы по сигналу прерывания")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
    finally:
        stop_event.set()
        watchdog_thread.join(timeout=5)
        logger.info("Приложение завершено")


if __name__ == "__main__":
    main()
