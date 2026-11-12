#!/usr/bin/env bash
set -euo pipefail
PORT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
WZ_SOURCE="$PORT_DIR/../warzone2100"
mkdir -p "$PORT_DIR/build/tests"
# Compile the production implementation for the host with its Android branch.
# --wrap adds Bionic's flag validation before forwarding to the real resolver.
"${CXX:-g++}" -std=c++17 -O1 -g -DNDEBUG -D__ANDROID__ \
    -Wall -Wextra -ffunction-sections -fdata-sections -fsanitize=address,undefined \
    -I"$PORT_DIR/build/engine" -I"$WZ_SOURCE" -I"$WZ_SOURCE/lib/netplay/tcp" \
    -I"$WZ_SOURCE/3rdparty" -I"$WZ_SOURCE/3rdparty/expected/include" \
    -I"$WZ_SOURCE/3rdparty/optional-lite/include" -I"$WZ_SOURCE/3rdparty/fmt/include" \
    -I"$WZ_SOURCE/3rdparty/glm" -I"$WZ_SOURCE/3rdparty/json/include" \
    "$PORT_DIR/tests/tcp_resolver_test.cpp" \
    "${WZ_NETSOCKET_SOURCE:-$WZ_SOURCE/lib/netplay/tcp/netsocket.cpp}" \
    "$WZ_SOURCE/lib/netplay/error_categories.cpp" "$WZ_SOURCE/lib/netplay/tcp/sock_error.cpp" \
    -Wl,--gc-sections -Wl,--wrap=getaddrinfo -o "$PORT_DIR/build/tests/tcp_resolver_test"
"$PORT_DIR/build/tests/tcp_resolver_test"
