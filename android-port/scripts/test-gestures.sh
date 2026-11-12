#!/usr/bin/env bash
set -euo pipefail
PORT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$PORT_DIR/build/tests"
"${CXX:-g++}" -std=c++17 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
    -I"$PORT_DIR/../warzone2100/lib/sdl" "$PORT_DIR/tests/touch_gestures_test.cpp" \
    -o "$PORT_DIR/build/tests/touch_gestures_test"
"$PORT_DIR/build/tests/touch_gestures_test"
