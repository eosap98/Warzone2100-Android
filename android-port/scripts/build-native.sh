#!/usr/bin/env bash
set -euo pipefail
PORT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
WZ_SOURCE="$(cd -- "$PORT_DIR/../warzone2100" && pwd)"
WZ_SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}"
WZ_NDK="${ANDROID_NDK_HOME:-$WZ_SDK/ndk/27.2.12479018}"
WZ_CMAKE="$PORT_DIR/build/host-tools/cmake/data/bin/cmake"
WZ_PREFIX="$PORT_DIR/build/prefix"
python3 "$PORT_DIR/scripts/prepare-revision.py"
export PKG_CONFIG_LIBDIR="$WZ_PREFIX/lib/pkgconfig"
export PKG_CONFIG_PATH="$PKG_CONFIG_LIBDIR"
"$WZ_CMAKE" -S "$WZ_SOURCE" -B "$PORT_DIR/build/engine" -G Ninja \
  -DCMAKE_MAKE_PROGRAM="$WZ_SDK/cmake/3.22.1/bin/ninja" \
  -DCMAKE_TOOLCHAIN_FILE="$WZ_NDK/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-26 -DANDROID_STL=c++_shared \
  -DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DCMAKE_BUILD_TYPE=Release '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG' \
  '-DCMAKE_C_FLAGS_RELEASE=-O2 -DNDEBUG' -DCMAKE_PREFIX_PATH="$WZ_PREFIX" \
  -DZLIB_LIBRARY="$WZ_PREFIX/lib/libz.a" -DZLIB_LIBRARY_RELEASE="$WZ_PREFIX/lib/libz.a" -DZLIB_LIBRARY_DEBUG="$WZ_PREFIX/lib/libz.a" -DCMAKE_FIND_ROOT_PATH="$WZ_PREFIX" -DCMAKE_INSTALL_PREFIX="$PORT_DIR/build/install" \
  -DCURL_CONFIG_EXECUTABLE="$WZ_PREFIX/bin/curl-config" \
  -DENABLE_NLS=ON -DIntl_INCLUDE_DIR="$WZ_PREFIX/include" -DIntl_LIBRARY="$WZ_PREFIX/lib/libintl.a" \
  -DENABLE_DOCS=OFF -DENABLE_DISCORD=OFF \
  -DENABLE_GNS_NETWORK_BACKEND=OFF -DWZ_ENABLE_BACKEND_VULKAN=OFF \
  -DWZ_USE_SYSTEM_LIBJPEG_TURBO=ON -DWZ_ENABLE_WARNINGS_AS_ERRORS=OFF -DWZ_ENABLE_WARNINGS=OFF \
  -DWZ_DISTRIBUTOR=AndroidNativePort -DWZ_DATADIR=data \
  "$@"
"$WZ_CMAKE" --build "$PORT_DIR/build/engine" --target warzone2100 -j "${JOBS:-3}"
python3 "$PORT_DIR/scripts/prepare-revision.py" --verify-build
