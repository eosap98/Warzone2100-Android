# Verifikasi paket — 12 November 2026

Snapshot aplikasi: **4.7.0-android.6**, versionCode **4070006**.

- Patch diregenerasi dari working tree terbaru, termasuk 5 file baru yang belum masuk Git.
- Rekonstruksi dari commit upstream menghasilkan seluruh 18 file modifikasi yang identik byte demi byte dengan source terbaru.
- Uji integrasi setup pada lokasi terpisah berhasil menerapkan patch dari checkout tanpa patch, memeriksa 16 submodule, dan mempertahankan protokol multiplayer 16384/104.
- Uji source hasil pemulihan lulus: 48 skenario gestur dan 10.000 peristiwa campuran, dengan AddressSanitizer/UndefinedBehaviorSanitizer.
- SHA-256 19 arsip dependensi cocok dengan dependencies.lock.json.
- Paket data Debian 4.7.0 cocok dengan inputs.lock.json; URL unduhan resmi merespons HTTP 200 saat diperiksa.
- APK terakhir cocok dengan SHA-256 d7662f692fb77945a888ed75e9aa6adea6e0ea174628676eb537e5f2d5b6383a.
- Seluruh skrip Python dan shell lolos pemeriksaan sintaks. Pemeriksaan SDK/NDK/JDK lulus memakai toolchain yang tersedia di PC asal.
- Audit folder publik dan simulasi git add tidak menemukan APK, paket Debian, arsip aset game, source upstream lengkap, cache build, atau kunci penandatanganan. File terbesar berada di bawah batas 100 MiB GitHub.

Penyesuaian untuk pemindahan hanya dilakukan pada salinan paket: lokasi SDK mengikuti home pengguna/variabel lingkungan, alias libtool dibedakan berdasarkan lokasi proyek, shell dipanggil melalui bash, serta ditambahkan skrip setup/pemeriksaan input dan panduan PC baru. Source engine dan fitur aplikasi tetap sama dengan snapshot asli.

Build penuh belum dijalankan ulang pada PC tujuan. Laporan APK tanggal 10 November 2026 adalah hasil build sebelumnya. Gameplay belum diuji pada perangkat fisik.
