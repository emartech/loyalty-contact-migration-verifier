#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 SAP Engagement Cloud
# SPDX-License-Identifier: MIT
#
# Launcher for Loyalty CSV Verifier (macOS / Linux)
# Usage: bash run-mac.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv-web"

# --- locate Python 3 ---
find_python() {
    for candidate in python3 python; do
        if command -v "$candidate" &>/dev/null; then
            version=$("$candidate" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
            if [ "$version" -ge 3 ] 2>/dev/null; then
                echo "$candidate"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON=$(find_python || true)

if [ -z "$PYTHON" ]; then
    echo "Python 3 not found. Attempting automatic installation..."
    if command -v brew &>/dev/null; then
        echo "Installing Python 3 via Homebrew..."
        brew install python
        PYTHON=$(find_python || true)
    fi

    if [ -z "$PYTHON" ]; then
        echo ""
        echo "ERROR: Python 3 could not be installed automatically."
        echo ""
        echo "Install it with Homebrew:  brew install python"
        echo "Or download from:          https://www.python.org/downloads/"
        echo ""
        exit 1
    fi
fi

echo "Using $($PYTHON --version)"

# --- create venv if it doesn't exist ---
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# --- install dependencies into the venv if missing ---
if ! "$VENV_PYTHON" -c "import flask" &>/dev/null 2>&1; then
    echo "Installing flask..."
    "$VENV_PIP" install flask --quiet
    echo "Dependencies installed."
fi

# --- launch ---
echo "Starting Loyalty CSV Verifier..."
exec "$VENV_PYTHON" "$SCRIPT_DIR/server.py"
