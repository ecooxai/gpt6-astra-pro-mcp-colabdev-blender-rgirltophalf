#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export LIBGL_ALWAYS_SOFTWARE=1
export OMP_NUM_THREADS=8
exec xvfb-run -a -s '-screen 0 1280x1024x24' /home/dev/.local/opt/blender-4.2.3-linux-x64/blender -b -t 8 --factory-startup --python src/build.py -- "$@"
