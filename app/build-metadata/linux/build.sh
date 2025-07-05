#!/bin/bash

# A script to build a Linux executable from a Python script using PyInstaller.

PYTHON_SCRIPT="app/main.py"
APP_NAME="FastApp"

echo "--- Bundling with PyInstaller ---"
# Check if the Python script and icon exist.
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT' not found."
    exit 1
fi

poetry run pyinstaller --name "$APP_NAME" --windowed --onefile --clean "$PYTHON_SCRIPT"

echo "✅ Build complete!"