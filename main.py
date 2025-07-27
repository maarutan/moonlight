#!/usr/bin/env python

from fabric import Application
from fabric.utils import get_relative_path

from modules import ScreenCorners, ActivateLinux, StatusBar, NotificationPopup
from config import APP_NAME

corners = ScreenCorners()
activate_linux = ActivateLinux()
bar = StatusBar()
# notification = NotificationPopup()

corners.set_visible(True)
app = Application(
    f"{APP_NAME}",
    corners,
    activate_linux,
    bar,
    # notification,
)


def set_css():
    app.set_stylesheet_from_file(
        get_relative_path("main.css"),
    )


def main():
    app.set_css = set_css
    app.set_css()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
