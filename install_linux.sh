#!/usr/bin/env bash
set -euo pipefail

echo "== Chromebook/Linux setup =="

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install it with your Chromebook Linux package manager."
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r linux_requirements.txt

if command -v apt-get >/dev/null 2>&1; then
  echo "Installing Tesseract OCR..."
  sudo apt-get update
  sudo apt-get install -y tesseract-ocr
else
  echo "apt-get was not found. Install the 'tesseract-ocr' package with your distro package manager."
fi

echo
echo "Setup complete."
echo "Run: bash run_linux.sh"
