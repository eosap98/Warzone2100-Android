#!/usr/bin/env bash
set -euo pipefail
# Sourced by build-apk.sh; can also be run directly to check a new PC.
export ANDROID_HOME="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}"
export ANDROID_NDK_HOME="${ANDROID_NDK_HOME:-$ANDROID_HOME/ndk/27.2.12479018}"
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-21-openjdk-amd64}"
for tool in python3 git curl make pkg-config gcc g++ dpkg-deb; do
    command -v "$tool" >/dev/null || { echo "Prasyarat belum tersedia: $tool. Baca BUILD-PC-BARU.md." >&2; exit 1; }
done
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || {
    echo 'Build ini memerlukan Linux x86_64 (Ubuntu 24.04 / WSL2 Ubuntu).' >&2; exit 1;
}
python3 -c 'import sys; assert sys.version_info >= (3, 12), "Memerlukan Python 3.12+"'
python3 -m pip --version >/dev/null
for path in \
    "$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake" \
    "$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang" \
    "$ANDROID_HOME/platforms/android-35/android.jar" \
    "$ANDROID_HOME/build-tools/35.0.0/aapt" \
    "$ANDROID_HOME/build-tools/35.0.0/d8" \
    "$ANDROID_HOME/build-tools/35.0.0/apksigner" \
    "$ANDROID_HOME/build-tools/35.0.0/zipalign" \
    "$ANDROID_HOME/cmake/3.22.1/bin/ninja" \
    "$JAVA_HOME/bin/javac" "$JAVA_HOME/bin/keytool"; do
    [[ -f "$path" ]] || { echo "Prasyarat belum tersedia: $path. Baca BUILD-PC-BARU.md." >&2; exit 1; }
done
echo 'OK: prasyarat host, Android SDK, NDK, dan JDK tersedia.'
