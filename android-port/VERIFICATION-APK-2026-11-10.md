# Verifikasi build APK Warzone 2100 Android

Build dan pemeriksaan statis lulus. Gameplay belum diuji di perangkat fisik.

- APK: `Warzone2100-4.7.0-android-arm64.apk`
- Versi: `4.7.0-android.6` (versionCode 4070006).
- Ukuran: 420954616 byte (401.5 MiB)
- SHA-256: `d7662f692fb77945a888ed75e9aa6adea6e0ea174628676eb537e5f2d5b6383a`
- Minimum Android 8.0 (API 26); target SDK 35; ARM64; OpenGL ES 3.0.
- Seluruh 123 berkas data cocok dengan manifest SHA-256.
- CRC ZIP APK, base.wz, dan mp.wz lulus.
- Tanda tangan dan zipalign diperiksa oleh `package-apk.py`; log: `apk-build.log`.
- SDL_main dan JNI nativePauseAudio diperiksa saat pengemasan.
- Simbol GNU gettext ada dalam engine ARM64; 59 katalog bahasa/guide dapat dibaca.
- Uji bahasa pada host: 715 pemeriksaan, termasuk 140 pergantian bahasa, UTF-8, konteks, guide, plural, dan angka desimal; log: language-tests.log.
- Protokol multiplayer: 16384/104, sesuai Warzone 2100 4.7.0 PC. Build menolak metadata tag yang tidak lengkap.
- Uji jaringan host memakai kode resolver/socket asli dengan validasi flag Android: IPv4, fixture IPv6, failover alamat, transfer TCP, dan propagasi error DNS; log: network-tests.log.
- Tautan GitHub tujuan terverifikasi di DEX: https://github.com/eosap98/Warzone2100-Android.
- Uji recognizer gestur: 48 skenario dan 10.000 peristiwa campuran dengan AddressSanitizer/UndefinedBehaviorSanitizer; hasil: gesture-tests.log.
- Rotasi dua jari: geser kiri/kanan, putar melingkar, zoom bersamaan, batas sudut, pergantian jari, dan pembatalan diuji pada host. Panduan rotasi terverifikasi di DEX.
- Pustaka dinamis yang dibutuhkan tersedia dalam APK atau API sistem Android.

- base.wz: 3362 entries, CRC OK
- mp.wz: 619 entries, CRC OK
- lib/arm64-v8a/libSDL3.so: AArch64, LOAD alignment 16384, 16384, 16384
- lib/arm64-v8a/libc++_shared.so: AArch64, LOAD alignment 16384, 16384, 16384, 16384
- lib/arm64-v8a/libwarzone2100.so: AArch64, LOAD alignment 16384, 16384, 16384

Tidak ada emulator yang digunakan. Instalasi, rendering, audio, kontrol, save/load, kampanye, multiplayer, dan suspend/resume masih memerlukan pengujian di perangkat ARM64 nyata.
