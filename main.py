#!/usr/bin/env python
import signal
import sys
import os

from fabric import Application
from fabric.utils import get_relative_path, exec_shell_command_async
from services import CheckConfig

from modules import (
    ScreenCorners,
    ActivateLinux,
    StatusBar,
    NotificationPopup,
    Dock,
    PlayerWrapper,
    DesktopClock,
    LanguagePreview,
)
from config import APP_NAME

corners = ScreenCorners()
activate_linux = ActivateLinux()
bar = StatusBar()
language = LanguagePreview()

corners.set_visible(True)
app = Application(
    f"{APP_NAME}",
    corners,
    activate_linux,
    bar,
    DesktopClock(),
    language,
    # PlayerWrappe(),
    # Dock(),
    # notification,
)


def set_css():
    app.set_stylesheet_from_file(
        get_relative_path("main.css"),
    )


def restart_program(signum, frame):
    print("[INFO] Received SIGHUP, restarting application...")
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def on_config_changed():
    print("[INFO] Config changed signal received")
    app.set_css()

    restart_program(None, None)


def main():
    app.set_css = set_css
    app.set_css()

    signal.signal(signal.SIGHUP, restart_program)

    check_config = CheckConfig()
    check_config.connect("config-changed", on_config_changed)

    app.run()


if __name__ == "__main__":
    try:
        main()
        exec_shell_command_async("./sass.sh")
    except Exception as e:
        print(f"[ERROR] {e}")
