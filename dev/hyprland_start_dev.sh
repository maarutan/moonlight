#!/usr/bin/env bash

project_dir="$(dirname "$(dirname "$(realpath "$0")")")"
sass_compiler_path="$project_dir""/sass.sh -w"

# start
setsid "$sass_compiler_path"
cd  "$project_dir" || exit
source "$project_dir"/.venv/bin/activate
nvim "$project_dir"/"main.py"
yazi "$project_dir"


