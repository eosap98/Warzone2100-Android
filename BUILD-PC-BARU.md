# Build di PC baru

Snapshot: **4.7.0-android.6**, dibuat **12 November 2026**. Target APK: `arm64-v8a`, minimum API 26, target SDK 35, OpenGL ES 3.0.

## 1. Sistem host

Gunakan **Ubuntu 24.04 x86_64**. Untuk Windows, gunakan **WSL2 dengan Ubuntu 24.04**, kemudian simpan proyek dan SDK di filesystem Linux seperti `~/projects/warzone-android`. Build Windows native dan macOS tidak didukung oleh skrip ini. Sediakan sekitar **25 GB ruang kosong** untuk SDK, source, data, dependensi, dan hasil kompilasi. Akses internet diperlukan untuk pemasangan toolchain dan input yang belum tersedia.

```bash
sudo apt update
sudo apt install -y build-essential git curl ca-certificates pkg-config \
  python3 python3-pip python3-venv openjdk-21-jdk zlib1g-dev \
  autoconf automake libtool gettext unzip zip xz-utils dpkg-dev
```

Versi yang dikunci: Python 3.12+, JDK 21, NDK **27.2.12479018**, platform Android **35**, build-tools **35.0.0**, SDK CMake **3.22.1** (untuk Ninja). CMake **3.31.6** diunduh otomatis melalui pip ke `android-port/build/host-tools`; tidak mengganti CMake sistem.

## 2. Android SDK

Pasang Android command-line tools untuk **Linux** dari <https://developer.android.com/studio#command-tools>. Ekstrak sehingga tersedia `~/Android/Sdk/cmdline-tools/latest/bin/sdkmanager`. Android Studio Linux juga dapat dipakai untuk memasang komponen SDK tersebut.

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export ANDROID_NDK_HOME="$ANDROID_HOME/ndk/27.2.12479018"
export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

sdkmanager --sdk_root="$ANDROID_HOME" --licenses
sdkmanager --sdk_root="$ANDROID_HOME" \
  "platform-tools" "platforms;android-35" "build-tools;35.0.0" \
  "cmake;3.22.1" "ndk;27.2.12479018"
```

Jika SDK berada di folder lain, sesuaikan `ANDROID_HOME` dan `ANDROID_NDK_HOME`. Gunakan SDK Linux saat bekerja dalam WSL2. Variabel di atas berlaku untuk terminal yang sedang digunakan; simpan pengaturannya di konfigurasi shell jika dibutuhkan.

## 3. Siapkan input

Ekstrak ZIP atau clone repository, lalu masuk ke folder yang berisi `build.sh`.

**Dari folder GitHub:**

```bash
bash setup.sh
```

Script mengambil source tag 4.7.0 dan memverifikasi commit, menerapkan patch terbaru, menyiapkan submodule kode, melengkapi tag untuk protokol multiplayer 16384/104, lalu mengunduh paket `warzone2100_ubuntu24.04_amd64.deb`. Paket Debian hanya dipakai sebagai sumber data portable; executable Linux dari paket tersebut tidak dijalankan atau dimasukkan ke APK.

**Dari backup pribadi:** source yang sudah dipatch, metadata Git/submodule, paket Debian, dan 19 arsip dependensi sudah tersedia. Cukup periksa:

```bash
bash setup.sh --check
```

Jika input tidak lengkap, `bash setup.sh` dapat mengambil input yang hilang. Script tidak menghapus checkout yang sudah ada. Kunci asli tersedia di `android-port/local-debug.keystore` hanya pada backup pribadi. Pertahankan file itu jika ingin APK baru dapat memperbarui instalasi yang memakai kunci lama.

## 4. Periksa dan build

```bash
bash android-port/scripts/build-env.sh
JOBS=3 bash build.sh
```

Turunkan `JOBS` ke 1–2 bila RAM terbatas. Pipeline membangun dependensi native dan engine, menjalankan uji gestur/jaringan/bahasa, mengekstrak data, mengompilasi Java/DEX, membuat APK, zipalign, menandatangani, dan memverifikasi hasil. Emulator tidak diperlukan.

Hasil berada di:

```text
Warzone2100-4.7.0-android-arm64.apk
Warzone2100-4.7.0-android-arm64.apk.sha256
android-port/VERIFICATION.md
android-port/*-build.log
```

Nama hasil APK tetap sama dengan APK referensi dalam backup; salin APK referensi jika ingin menyimpannya terpisah sebelum build.

## 5. Pemindahan dan pemeriksaan

Cache kompilasi tidak disertakan karena CMake dan libtool menyimpan lokasi absolut. Jangan menyalin cache `build/engine`, `build/prefix`, atau `build/deps` dari PC lama. Backup hanya membawa `build/downloads`, yang berisi arsip sumber dependensi dan aman untuk dipakai di lokasi baru. SDK, NDK, JDK, paket sistem, dan instalasi pip CMake perlu dipasang pada PC baru; backup ini bukan image sistem build offline.

ZIP mempertahankan metadata izin dan symbolic link. Ekstrak backup di Ubuntu/WSL dengan `unzip`, bukan ke filesystem Windows. Pemanggilan `bash build.sh` tetap dapat digunakan jika izin eksekusi shell hilang saat dipindahkan.

Untuk ZIP backup, cocokkan SHA-256 dengan file `.sha256` di sampingnya sebelum ekstraksi. Di dalam backup tersedia `MANIFEST-SHA256.json` dan `verify-backup.py`; jalankan `python3 verify-backup.py` segera setelah ekstraksi, sebelum build mengubah/membuat file.

Laporan pengujian APK tanggal 10 November 2026 disertakan sebagai referensi. Pembuatan paket backup memeriksa rekonstruksi patch dan integritas arsip; belum menjalankan build penuh pada PC baru atau pengujian gameplay pada perangkat fisik.
