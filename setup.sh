#!/usr/bin/env bash
set -euo pipefail
WZ_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$WZ_ROOT/tools/prepare-inputs.py" "$@"
