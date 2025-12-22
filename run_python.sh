#!/bin/bash
# Helper script to run Python commands with the correct virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use the venv python explicitly
exec ./.venv/bin/python "$@"
