#!/usr/bin/env bash
set -euo pipefail
WZ_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$WZ_ROOT/tools/prepare-inputs.py" --check
exec bash "$WZ_ROOT/android-port/build-apk.sh" "$@"
