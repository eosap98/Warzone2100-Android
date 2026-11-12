#!/usr/bin/env bash
set -euo pipefail
PORT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$PORT_DIR/build/tests"
python3 "$PORT_DIR/scripts/build-host-gettext.py"
WZ_HOST_GETTEXT="$PORT_DIR/build/host-gettext"
"${CXX:-g++}" -std=c++17 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
    -I"$WZ_HOST_GETTEXT/include" \
    -I"$PORT_DIR/../warzone2100/lib/framework" "$PORT_DIR/tests/android_locale_test.cpp" \
    "$WZ_HOST_GETTEXT/lib/libintl.a" \
    -o "$PORT_DIR/build/tests/android_locale_test"
"$PORT_DIR/build/tests/android_locale_test" "$PORT_DIR/build/assets/data/locale"
