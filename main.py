#!/usr/bin/env python
#                            M O O N L I G H T
#      _..._         _..._         _..._         _..._         _..._
#    .:::::::.     .::::. `.     .::::  `.     .::'   `.     .'     `.
#   :::::::::::   :::::::.  :   ::::::    :   :::       :   :         :
#   :::::::::::   ::::::::  :   ::::::    :   :::       :   :         :
#   `:::::::::'   `::::::' .'   `:::::   .'   `::.     .'   `.       .'
#     `':::''       `'::'-'       `'::.-'       `':..-'       `-...-'
#
# ---------------------------------------------------------------------->
# ┌┬┐┌─┐┌─┐┌┐┌┬  ┬┌─┐┬ ┬┌┬┐
# ││││ ││ │││││  ││ ┬├─┤ │
# ┴ ┴└─┘└─┘┘└┘┴─┘┴└─┘┴ ┴ ┴
# ---------------------------------->
# -------------------------->
#
# Copyright (c) 2025 maarutan. \ Marat Arzymatov All Rights Reserved.
# Author: Marat Arzymatov \ maarutan
# Github.com: https://github.com/maarutan
# License: MIT
#


import os
import sys
import signal
from loguru import logger
from modules.handler import Handler
from fabric.utils.helpers import idle_add


def restart():
    try:
        logger.info("\n\nRestarting Moonlight...\n")
        Handler.app.quit()
    except Exception as e:
        logger.warning(f"\nGraceful quit failed: {e}")
    finally:
        os.execv(sys.executable, [sys.executable] + sys.argv)


def handle_sighup(*_):
    idle_add(restart)


def main():
    signal.signal(signal.SIGHUP, handle_sighup)
    Handler.app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Handler.app.quit()
    except Exception as e:
        logger.error(f"Failed to run the application: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------->
# ---------------------------------------------------------------------->
# -------------------------------------------------------------->
# ----------------------------------------------->
