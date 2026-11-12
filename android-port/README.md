# Warzone 2100 — port native Android

Port lokal Warzone 2100 **4.7.0-android.6** (versionCode `4070006`), dari commit `7d3d8e51a61ceee89e6bf672a41337e1a9cd7392`. Sumber berada di `../warzone2100`, cabang `android-native`, dengan data game dari paket Debian 4.7.0. Metadata semua tag rilis ikut diambil agar nomor protokol multiplayer sama dengan rilis PC meskipun checkout memakai shallow clone.

Perubahan terbaru android.6: **kamera dapat diputar dengan dua jari** pada medan permainan. Sentuh dengan dua jari, lalu geser bersama ke kiri/kanan atau putar kedua jari melingkar. Geser horizontal memakai sensitivitas kontrol mouse desktop (0,25 derajat per piksel logis); gerakan melingkar mengikuti sudut kedua jari. Rotasi hanya mengubah arah kamera, tanpa mengubah kemiringannya. Panduan kontrol pada launcher juga diperbarui.

Gerakan dua jari dihitung setelah seluruh event sentuh satu frame dibaca agar posisi jari yang diperbarui bergantian tidak memicu zoom atau rotasi palsu. Ambang gerak membedakan tap, geser, cubit, dan putaran; cubit dan gerakan melingkar dapat dipakai bersamaan. Rotasi tidak mengirim perintah unit dan berhenti saat salah satu jari dilepas. Sudut melewati batas satu putaran dengan mulus, sedangkan jari yang berhimpitan atau bertukar sisi tidak membuat kamera tiba-tiba berputar setengah lingkaran. **48 skenario gestur dan 10.000 peristiwa campuran** lulus dengan AddressSanitizer/UndefinedBehaviorSanitizer pada host Linux (`gesture-tests.log`). Build dan uji tidak menggunakan emulator; kontrol di perangkat fisik belum diuji.

Perbaikan dari build sebelumnya:

- Error **Failed to open connection: invalid value for ai_flags** saat join multiplayer diperbaiki. Bionic Android menolak `AI_V4MAPPED` meskipun konstanta tersedia di header NDK. Resolver Android kini tidak mengirim flag tersebut; `AF_UNSPEC` tetap mendukung IPv4 dan IPv6. Uji memakai implementasi asli `netsocket.cpp` dengan validasi flag Android pada host Linux: versi lama gagal untuk `127.0.0.1` (`network-before.log`), sedangkan versi baru lulus 56 pemeriksaan IPv4, localhost, alamat cadangan, fixture IPv6, transfer TCP loopback, dan propagasi error DNS dengan sanitizer (`network-tests.log`). Join/gameplay pada ponsel belum diuji.
- **Panduan kontrol | Port by** berada dalam satu baris di tengah layar, dengan lebar kedua sisi sama dan garis pemisah 24 dp tepat di tengah.
- Layar pembuka memakai latar gelap dengan aksen emas, judul WARZONE 2100 di tengah agak ke atas, tombol mulai yang jelas, indikator persiapan data, serta panduan kontrol dalam dialog. Tata letak menyesuaikan ukuran layar, cutout, dan ukuran font.
- Logo GitHub dan area kredit membuka **https://github.com/eosap98/Warzone2100-Android** di browser.
- NLS diaktifkan dengan GNU gettext 0.22.5 dan libiconv 1.17. Sebanyak 59 katalog terjemahan game/guide disertakan. Pergantian bahasa memakai `LANGUAGE` dan locale `C.UTF-8` yang tersedia di Android, menyegarkan cache gettext, serta menyimpan kode pilihan bahasa yang benar. Ubah bahasa melalui pengaturan antarmuka pada menu utama game.
- Protokol multiplayer diperbaiki dari `16384/1` menjadi `16384/104`, sesuai PC 4.7.0. Penyebabnya adalah clone lama hanya mempunyai satu tag, sedangkan upstream menghitung protokol dari urutan tag. `prepare-revision.py` mengambil metadata tag dan memeriksa hasil kompilasi; filter kompatibilitas serta pemeriksaan versi game tetap digunakan.

Pemeriksaan HTTPS lobby resmi pada 10 November 2026 mengembalikan **16 host**, semuanya cocok dengan protokol baru dan mendukung TCP. Protokol lama tidak cocok dengan satu pun host tersebut. Hasil dan waktu pemeriksaan tersimpan di `lobby-verification.json`; jumlah host dapat berubah. Pemeriksaan ini dijalankan dari PC dan belum membuktikan join/gameplay pada ponsel.

Engine C/C++ dikompilasi ulang menjadi `libwarzone2100.so` dengan Android NDK. SDL3 mengelola aktivitas, permukaan OpenGL ES, dan input Android; OpenAL Soft memakai OpenSL ES. APK memuat engine native ARM64 dan data game. Tidak memakai emulator, Wine, Box64, proot, WebView, atau menjalankan executable Linux dari `.deb`.

Patch engine tersedia di `warzone2100-android.patch`; revisi sumber dan submodule tercatat di `source-revisions.txt`. Hasil APK terakhir ada di `VERIFICATION-APK-2026-11-10.md`; build baru menghasilkan `VERIFICATION.md`.

**Target:** Android 8.0/API 26 atau lebih baru, `arm64-v8a`, OpenGL ES 3.0. Target SDK 35. Build memakai NDK 27.2.12479018 dan alignment segmen native 16 KB. Build ini belum dijalankan pada perangkat fisik.

APK hasil build berada satu folder di atas direktori ini: `Warzone2100-4.7.0-android-arm64.apk`. APK ditandatangani dengan kunci build lokal `local-debug.keystore`; simpan kunci tersebut jika ingin memperbarui instalasi yang sama. Ini build pengembangan lokal, bukan rilis resmi Warzone 2100.

Paket ini berisi revisi android.6. Riwayat backup versi lama tidak disertakan.

**Pemakaian:** pasang APK, buka Warzone 2100, tunggu pemeriksaan/penyalinan data pertama selesai, lalu tekan MULAI GAME. Sediakan sekitar 1 GB ruang kosong untuk APK dan data yang diekstrak. Data kampanye, skirmish, mod bawaan paket, musik, font, dan tekstur dari `.deb` disertakan. Paket Debian ini tidak berisi video sinematik terpisah.

- **Geser satu jari:** menggeser kamera.
- **Tap satu jari:** memberi perintah gerak/aksi kepada unit yang sudah dipilih.
- **Tap dua jari bersamaan:** melepas seluruh pilihan.
- **Geser dua jari bersama ke kiri/kanan:** memutar kamera ke kiri/kanan.
- **Putar dua jari melingkar:** memutar kamera mengikuti gerakan kedua jari; dapat digabung dengan cubit untuk zoom.
- **Tahan satu jari sekitar 0,42 detik lalu seret:** membuat kotak seleksi; lepaskan untuk memilih unit di dalamnya.
- **Tap dua kali pada unit:** memilih hanya unit tersebut. Jarak antartap maksimal sekitar 0,3 detik.
- **Cubit dua jari:** zoom masuk/keluar; jari yang tersisa setelah cubit atau rotasi tidak berubah menjadi tap atau geser.
- **Tombol kembali Android:** membuka menu game.
- **Menu/HUD game:** tap biasa, slider dan drag tetap memakai klik kiri. Penempatan bangunan tetap memakai tap.
- Keyboard dan mouse fisik tetap memakai input SDL biasa. Kolom teks menggunakan keyboard Android.

Bilah shortcut Android di atas layar sudah dihapus. Layar pembuka menampilkan **Port by [logo GitHub] EosAP98 (aka AsfatreHilmi)**. Logo memakai GitHub Octicons `mark-github-16`; SVG asli dan lisensinya berada di `app/artwork/`.

Tap pada medan permainan menunggu sekitar 0,3 detik untuk membedakannya dari double-tap, sehingga tap pertama pada unit tidak lebih dulu mengirim perintah. Geser, cubit, rotasi, pembatalan sentuhan, dan kehilangan fokus membatalkan tap tertunda. Uji logika gestur tersedia di `scripts/test-gestures.sh`; 48 skenario dan 10.000 peristiwa campuran diperiksa dengan AddressSanitizer/UndefinedBehaviorSanitizer pada host Linux, tanpa emulator. Uji mencakup arah rotasi, dua putaran penuh, batas sudut, susunan/urutan jari, rotasi dan zoom bersamaan, gerakan kecil saat tap, penggantian jari, pembatalan, serta kontrol lama.

Uji bahasa di `scripts/test-languages.sh` menjalankan kode pemilihan katalog Android terhadap katalog yang benar-benar dikemas: 715 pemeriksaan termasuk 140 pergantian bahasa, kembali ke bahasa Inggris, UTF-8, konteks, guide, plural Rusia, dan angka desimal. Uji memakai GNU gettext 0.22.5 yang dibangun untuk host, sama versinya dengan runtime APK; gettext bawaan glibc terbaru memiliki perilaku `C.UTF-8` yang berbeda. Biner host hanya digunakan untuk uji dan tidak dimasukkan ke APK.

Konfigurasi awal memakai klik kanan untuk perintah, grafik terrain classic, bayangan dimatikan, dan ukuran UI disesuaikan dengan layar. Pengaturan dapat diubah melalui menu game. Data, konfigurasi, dan save disimpan pada direktori privat aplikasi (`files/data` dan `files/config`). Uninstall akan menghapus direktori tersebut. Simpan game melalui menu sebelum keluar; penghentian proses oleh Android tidak menjamin autosave.

**Build di PC baru:**

Ikuti [BUILD-PC-BARU.md](../BUILD-PC-BARU.md) untuk menyiapkan SDK dan input build.

```bash
bash setup.sh --check
bash build.sh
```

Prasyarat host: Python 3.12+ dengan pip, Git, curl, make, pkg-config, gcc/g++ dengan ASan/UBSan dan header zlib, JDK 21, Android SDK platform 35/build-tools 35.0.0/CMake 3.22.1 untuk Ninja, dan NDK 27.2.12479018. CMake 3.31.6 dipasang lokal ke direktori build. Lokasi SDK/NDK/JDK dapat diatur melalui `ANDROID_HOME`, `ANDROID_NDK_HOME`, dan `JAVA_HOME`; `JOBS` menentukan paralelisme kompilasi (default 3).

Skrip memvalidasi hash sumber dependensi terhadap `dependencies.lock.json`, membangun pustaka native, mengekstrak aset portable dari `.deb`, mengompilasi Java/DEX, mengemas, melakukan zipalign, lalu menandatangani dan memverifikasi APK. Tidak ada tahapan yang menjalankan emulator. Cache berada di `build/`; jika mengubah opsi kompilasi suatu dependensi, hapus stamp `.nama-installed` pada `build/prefix/` untuk membangunnya kembali.

Uji regresi koneksi dijalankan otomatis setelah kompilasi native. Untuk menjalankannya sendiri: `bash android-port/scripts/test-network.sh` dari folder workspace. Seluruh socket uji menggunakan loopback lokal; fixture IPv6 memodelkan jaringan dengan IPv6 aktif tanpa bergantung pada konfigurasi alamat eksternal PC.

Pemeriksaan lobby langsung bersifat terpisah dari build agar build berikutnya tidak bergantung pada tersedianya server lobby: `python3 android-port/scripts/check-lobby.py` dari folder workspace. Pemeriksaan integritas APK mencakup katalog bahasa, tujuan GitHub dalam DEX, protokol rilis, dan hash engine dalam `assets/build-info.json`.

Untuk memasang melalui USB pada perangkat yang sudah mengizinkan debugging:

```bash
adb install -r 'Warzone2100-4.7.0-android-arm64.apk'
```

Untuk diagnosis perangkat, ambil `adb logcat` ketika menjalankan game. Symbol engine disimpan pada `build/engine/src/` apabila dihasilkan oleh CMake upstream.

**Lingkup build:** OpenGL ES, backend jaringan TCP bawaan, audio native, dan gettext/NLS diaktifkan. Vulkan, Discord, serta backend GameNetworkingSockets tidak dibangun. Bahasa awal engine mengikuti locale Android; pilihan bahasa dapat diubah dan disimpan melalui menu game. Launcher dan petunjuk kontrol memakai bahasa Indonesia. Sebagian teks terjemahan upstream yang belum lengkap tetap memakai bahasa Inggris. Kinerja GPU, kampanye, multiplayer, save/load, input, serta suspend/resume belum divalidasi di perangkat fisik.

Lisensi Warzone dan pustaka pihak ketiga disertakan dalam aset APK. Modifikasi engine ada di patch; `setup.sh` mengambil source upstream saat diperlukan. Warzone dengan transcoder Basis Universal menggunakan GPLv3; baca `../warzone2100/pkg/licenses/COPYING.gpl3` serta lisensi aset/pustaka terkait sebelum mendistribusikan.
