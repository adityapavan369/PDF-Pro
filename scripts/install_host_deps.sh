#!/usr/bin/env bash
set -euo pipefail

# Install system deps for high-fidelity DOCX -> PDF conversions and visual diffs.
# Intended to be run on an Ubuntu host (or CI runner) with sudo privileges.

echo "Installing apt packages (LibreOffice)..."
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  libreoffice-common libreoffice-core-nogui libreoffice-writer libreoffice-draw \
  fonts-dejavu-core poppler-utils
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*

echo "Installing Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pymupdf Pillow

echo "Host dependencies installed."
