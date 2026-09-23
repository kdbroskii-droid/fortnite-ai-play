#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  echo "Virtual environment not found."
  echo "Run: bash install_linux.sh"
  exit 1
fi

source .venv/bin/activate
exec python linux_runner.py
