#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 src/server.py --port "${PORT:-8776}" --host "${HOST:-0.0.0.0}"
