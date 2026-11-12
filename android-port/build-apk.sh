#!/usr/bin/env bash
set -euo pipefail
PORT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$PORT_DIR/scripts/build-env.sh"
if [[ ! -x "$PORT_DIR/build/host-tools/cmake/data/bin/cmake" ]]; then
    python3 -m pip install --target "$PORT_DIR/build/host-tools" cmake==3.31.6
fi
git -C "$PORT_DIR/../warzone2100" submodule update --init --depth 1 --jobs "${JOBS:-3}" -- \
    3rdparty/utf8proc 3rdparty/glm 3rdparty/utfcpp 3rdparty/launchinfo \
    3rdparty/re2 3rdparty/EmbeddedJSONSignature 3rdparty/date 3rdparty/SQLiteCpp \
    3rdparty/readerwriterqueue 3rdparty/fmt 3rdparty/quickjs-wz 3rdparty/basis_universal \
    3rdparty/libplum 3rdparty/expected lib/sound/3rdparty/opusfile lib/netplay/3rdparty/miniupnp
python3 "$PORT_DIR/scripts/build-deps.py" 2>&1 | tee "$PORT_DIR/deps-build.log"
bash "$PORT_DIR/scripts/test-gestures.sh" 2>&1 | tee "$PORT_DIR/gesture-tests.log"
bash "$PORT_DIR/scripts/build-native.sh" 2>&1 | tee "$PORT_DIR/native-build.log"
bash "$PORT_DIR/scripts/test-network.sh" 2>&1 | tee "$PORT_DIR/network-tests.log"
python3 "$PORT_DIR/scripts/prepare-data.py" 2>&1 | tee "$PORT_DIR/data-build.log"
bash "$PORT_DIR/scripts/test-languages.sh" 2>&1 | tee "$PORT_DIR/language-tests.log"
python3 "$PORT_DIR/scripts/package-apk.py" 2>&1 | tee "$PORT_DIR/apk-build.log"
python3 "$PORT_DIR/scripts/verify-apk.py" 2>&1 | tee "$PORT_DIR/verification.log"
