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

import os, sys, signal
from modules import ModulesHandler

modules = ModulesHandler()
app = modules.Application


def handle_sighup(*_):
    os.execv(sys.executable, [sys.executable] + sys.argv)


def main():
    signal.signal(signal.SIGHUP, handle_sighup)
    modules.set_css()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")

# ---------------------------------------------------------------------------->
# ---------------------------------------------------------------------->
# -------------------------------------------------------------->
# ----------------------------------------------->
