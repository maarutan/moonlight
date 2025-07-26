#!/usr/bin/env bash

currentdir=$(dirname "$0")
execute="$currentdir"/main.py

source "$currentdir"/.venv/bin/activate

chmod +x "$execute"
python -u "$execute"
