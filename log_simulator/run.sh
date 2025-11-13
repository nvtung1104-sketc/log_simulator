#!/usr/bin/env bash
# Simple launcher for macOS / Linux: create venv (if needed), install deps and run app

set -euo pipefail

# run from script directory
cd "$(dirname "$0")"

# prefer python3, fallback to python
PY=python3
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python
fi

# create venv if missing
if [ ! -d ".venv" ]; then
  "$PY" -m venv .venv
fi

# activate venv
# shellcheck disable=SC1091
. .venv/bin/activate

# install requirements if present
if [ -f requirements.txt ]; then
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

# allow optional host/port params: ./run.sh [host] [port]
HOST="${1:-127.0.0.1}"
PORT="${2:-5000}"

echo "Starting Log Generator Simulator on ${HOST}:${PORT}..."
python app.py --host="$HOST" --port="$PORT"