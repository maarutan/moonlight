#!/usr/bin/env python

from fabric import Application
from fabric.utils import get_relative_path

from modules import StatusBar, ActivateLinux

from config import APP_NAME

bar = StatusBar()
activate_linux = ActivateLinux()

app = Application(
    f"{APP_NAME}",
    bar,
    activate_linux,
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
        print(e)
