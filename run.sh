#!/usr/bin/env bash
set -e
SCRIPT_PATH="./print_finished.py"
pipx run "$SCRIPT_PATH" "$@"