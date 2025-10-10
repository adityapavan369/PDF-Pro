#!/usr/bin/env bash
set -euo pipefail

# Install system deps for high-fidelity DOCX -> PDF conversions and visual diffs.
# Intended to be run on an Ubuntu host (or CI runner) with sudo privileges.

echo "Installing apt packages (LibreOffice)..."
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  libreoffice-core libreoffice-writer libreoffice-common libreoffice-draw libreoffice-pdfimport \
  fonts-dejavu-core poppler-utils

echo "Installing Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pymupdf Pillow

echo "Host dependencies installed."
