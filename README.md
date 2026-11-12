# Warzone 2100 Android — 4.7.0-android.6

Port native ARM64 untuk Android 8.0 atau lebih baru. Snapshot terbaru proyek lokal: **12 November 2026**, versionCode **4070006**. Perubahan terakhir menambahkan rotasi kamera dengan dua jari, melanjutkan perbaikan bahasa dan koneksi multiplayer.

Folder ini siap dijadikan repository GitHub. Isinya launcher Android, patch engine, skrip build, pengujian, lisensi, serta panduan. Source upstream lengkap, APK, paket Debian, aset game, cache kompilasi, dan kunci penandatanganan tidak disertakan. Ikon game diambil kembali dari upstream saat build.

## Build

Gunakan Linux x86_64; Ubuntu 24.04 atau WSL2 Ubuntu 24.04 di Windows disarankan. Proyek ini menggunakan skrip shell dan Android NDK; tidak menggunakan Gradle.

1. Ikuti [BUILD-PC-BARU.md](BUILD-PC-BARU.md) untuk memasang prasyarat.
2. Jalankan dari folder ini:

```bash
bash setup.sh
bash build.sh
```

`setup.sh` mengunduh source upstream pada commit yang dikunci, menerapkan patch Android, menyiapkan 16 submodule kode, melengkapi metadata versi multiplayer, lalu mengambil paket data resmi 4.7.0 dengan verifikasi SHA-256. Input yang diunduh otomatis diabaikan oleh Git. `bash setup.sh --check` hanya memeriksa input tanpa unduhan.

Hasil build: `Warzone2100-4.7.0-android-arm64.apk` di folder ini. Kunci lokal baru dibuat saat build pertama jika `android-port/local-debug.keystore` belum ada. Untuk memperbarui instalasi dari APK lama, salin kunci yang sama dari backup pribadi sebelum build.

## Isi

- [android-port/README.md](android-port/README.md): fitur, kontrol, batas pengujian, dan detail port.
- [android-port/warzone2100-android.patch](android-port/warzone2100-android.patch): seluruh 18 file perubahan engine terbaru, termasuk 5 file baru.
- [inputs.lock.json](inputs.lock.json): revisi upstream, submodule, hash patch, dan hash paket data.
- [android-port/dependencies.lock.json](android-port/dependencies.lock.json): 19 dependensi native dengan URL dan SHA-256.
- [android-port/VERIFICATION-APK-2026-11-10.md](android-port/VERIFICATION-APK-2026-11-10.md): hasil pengujian APK terakhir; bukan laporan build baru di PC tujuan.

## Upload ke GitHub

Jalankan dari folder ini setelah membuat repository kosong di GitHub:

```bash
git init -b main
git add .
git status --short
git commit -m "Add Warzone 2100 Android 4.7.0-android.6 port"
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

Ganti URL contoh dengan repository milik Anda. `.gitignore` sudah mengecualikan input game, hasil build, dan kunci lokal. Folder ini belum diunggah atau dihubungkan ke remote oleh proses pembuatan backup.

## Kredit dan lisensi

Warzone 2100 berasal dari [Warzone2100/warzone2100](https://github.com/Warzone2100/warzone2100), tag 4.7.0, commit `7d3d8e51a61ceee89e6bf672a41337e1a9cd7392`. Ini port lokal, bukan rilis resmi upstream. Kredit launcher: EosAP98 (aka AsfatreHilmi).

Lihat [LICENSE](LICENSE), pemberitahuan lisensi pada source/patch, serta [lisensi GitHub Octicons](android-port/app/artwork/OCTICONS-LICENSE.txt). Build menyertakan lisensi engine, aset, dan dependensi ke APK; lisensi komponen tetap berlaku masing-masing.
