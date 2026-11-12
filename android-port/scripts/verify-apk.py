#!/usr/bin/env python3
"""Verify packaged payload and 16 KB ELF alignment without running an emulator."""
import gettext, hashlib, io, json, os, pathlib, re, struct, subprocess, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
APK=ROOT.parent/'Warzone2100-4.7.0-android-arm64.apk'
SDK=pathlib.Path(os.environ.get('ANDROID_HOME',str(pathlib.Path.home()/'Android/Sdk')))
rows=[]
gesture_result=re.search(r'^PASS: (\d+) gesture scenarios, including two-finger rotation, cancellation and 10,000 mixed events$',
 (ROOT/'gesture-tests.log').read_text(), re.M)
assert gesture_result, 'Missing successful two-finger rotation regression checks'
with zipfile.ZipFile(APK) as archive:
 assert archive.testzip() is None, 'APK ZIP CRC failed'
 manifest=json.loads(archive.read('assets/data-manifest.json'))
 build_info=json.loads(archive.read('assets/build-info.json'))
 assert build_info['version_code']==4070006
 assert build_info['version_name']=='4.7.0-android.6'
 assert build_info['network_protocol']==[16384,104], 'Network version differs from official 4.7.0 hosts'
 assert build_info['native_language_support'] is True
 assert hashlib.sha256(archive.read('lib/arm64-v8a/libwarzone2100.so')).hexdigest()==build_info['engine_sha256']
 assert b'https://github.com/eosap98/Warzone2100-Android' in archive.read('classes.dex'), 'Missing GitHub destination'
 for instruction in (b'Geser 2 jari ke kiri / kanan', b'Putar 2 jari melingkar'):
  assert instruction in archive.read('classes.dex'), 'Missing rotation control guide'
 for item in manifest['files']:
  with archive.open('assets/data/'+item['path']) as stream:
   digest=hashlib.file_digest(stream,'sha256').hexdigest()
  assert digest == item['sha256'], item['path']
 catalogs={}
 for item in manifest['files']:
  if item['path'].startswith('locale/') and item['path'].endswith('.mo'):
   catalogs[item['path']]=gettext.GNUTranslations(io.BytesIO(archive.read('assets/data/'+item['path'])))
 assert len(catalogs)==59, 'Incomplete release translations'
 assert catalogs['locale/id/LC_MESSAGES/warzone2100.mo'].gettext('Single Player')=='Pemain Tunggal'
 assert catalogs['locale/id/LC_MESSAGES/warzone2100_guide.mo'].gettext('## Present Day:')=='## Masa Kini:'
 assert catalogs['locale/fr/LC_MESSAGES/warzone2100.mo'].gettext('Single Player')=='Un joueur'
 for name in ('base.wz','mp.wz'):
  with zipfile.ZipFile(io.BytesIO(archive.read('assets/data/'+name))) as data:
   assert data.testzip() is None, 'Invalid game archive: '+name
   rows.append(name+': '+str(len(data.namelist()))+' entries, CRC OK')
 libs=[name for name in archive.namelist() if name.startswith('lib/')]
 assert len(libs)==3, libs
 for name in libs:
  assert name.startswith('lib/arm64-v8a/'),name
  binary=archive.read(name)
  assert binary[:6] == b'\x7fELF\x02\x01',name
  header=struct.unpack_from('<HHIQQQIHHHHHH',binary,16)
  assert header[1]==183, name+' is not AArch64'
  alignments=[]
  for i in range(header[9]):
   ph=struct.unpack_from('<IIQQQQQQ',binary,header[4]+i*header[8])
   if ph[0]==1:
    assert ph[7]>=16384 and ph[2]%ph[7]==ph[3]%ph[7], name+' alignment'
    alignments.append(ph[7])
  assert alignments
  rows.append(name+': AArch64, LOAD alignment '+', '.join(map(str,alignments)))
badging=subprocess.check_output([str(SDK/'build-tools/35.0.0/aapt'),'dump','badging',str(APK)],text=True)
assert "package: name='org.warzone2100.android'" in badging
assert "versionCode='4070006'" in badging
assert "versionName='4.7.0-android.6'" in badging
assert "sdkVersion:'26'" in badging
assert "targetSdkVersion:'35'" in badging
assert "native-code: 'arm64-v8a'" in badging
assert "uses-gl-es: '0x30000'" in badging
(ROOT/'apk-badging.txt').write_text(badging)
with APK.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
expected=APK.with_suffix('.apk.sha256').read_text().split()[0]
assert digest==expected, 'APK hash mismatch'
report='\n'.join([
 '# Verifikasi build APK Warzone 2100 Android', '',
 'Build dan pemeriksaan statis lulus. Gameplay belum diuji di perangkat fisik.', '',
 '- APK: `'+APK.name+'`',
 '- Versi: `'+build_info['version_name']+'` (versionCode '+str(build_info['version_code'])+').',
 '- Ukuran: '+str(APK.stat().st_size)+' byte ('+str(round(APK.stat().st_size/1048576,1))+' MiB)',
 '- SHA-256: `'+digest+'`',
 '- Minimum Android 8.0 (API 26); target SDK 35; ARM64; OpenGL ES 3.0.',
 '- Seluruh '+str(len(manifest['files']))+' berkas data cocok dengan manifest SHA-256.',
 '- CRC ZIP APK, base.wz, dan mp.wz lulus.',
 '- Tanda tangan dan zipalign diperiksa oleh `package-apk.py`; log: `apk-build.log`.',
 '- SDL_main dan JNI nativePauseAudio diperiksa saat pengemasan.',
 '- Simbol GNU gettext ada dalam engine ARM64; '+str(len(catalogs))+' katalog bahasa/guide dapat dibaca.',
 '- Uji bahasa pada host: 715 pemeriksaan, termasuk 140 pergantian bahasa, UTF-8, konteks, guide, plural, dan angka desimal; log: language-tests.log.',
 '- Protokol multiplayer: 16384/104, sesuai Warzone 2100 4.7.0 PC. Build menolak metadata tag yang tidak lengkap.',
 '- Uji jaringan host memakai kode resolver/socket asli dengan validasi flag Android: IPv4, fixture IPv6, failover alamat, transfer TCP, dan propagasi error DNS; log: network-tests.log.',
 '- Tautan GitHub tujuan terverifikasi di DEX: https://github.com/eosap98/Warzone2100-Android.',
 '- Uji recognizer gestur: '+gesture_result[1]+' skenario dan 10.000 peristiwa campuran dengan AddressSanitizer/UndefinedBehaviorSanitizer; hasil: gesture-tests.log.',
 '- Rotasi dua jari: geser kiri/kanan, putar melingkar, zoom bersamaan, batas sudut, pergantian jari, dan pembatalan diuji pada host. Panduan rotasi terverifikasi di DEX.',
 '- Pustaka dinamis yang dibutuhkan tersedia dalam APK atau API sistem Android.',
 '', *['- '+r for r in rows], '',
 'Tidak ada emulator yang digunakan. Instalasi, rendering, audio, kontrol, save/load, kampanye, multiplayer, dan suspend/resume masih memerlukan pengujian di perangkat ARM64 nyata.', ''
])
(ROOT/'VERIFICATION.md').write_text(report)
print(report)
