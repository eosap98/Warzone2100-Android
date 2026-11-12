#!/usr/bin/env python3
"""Package with the official Android SDK tools; no Gradle or emulator is needed."""
import hashlib, json, os, pathlib, re, shutil, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'
SDK=pathlib.Path(os.environ.get('ANDROID_HOME',str(pathlib.Path.home()/'Android/Sdk')))
NDK=pathlib.Path(os.environ.get('ANDROID_NDK_HOME',str(SDK/'ndk/27.2.12479018')))
BT=SDK/'build-tools/35.0.0'
JAR=SDK/'platforms/android-35/android.jar'
JAVA=pathlib.Path(os.environ.get('JAVA_HOME','/usr/lib/jvm/java-21-openjdk-amd64'))/'bin'
LLVM=NDK/'toolchains/llvm/prebuilt/linux-x86_64/bin'
CLASSES=BUILD/'java-classes'
DEX=BUILD/'dex'
STAGE=BUILD/'apk'
for d in (CLASSES,DEX,STAGE): d.mkdir(parents=True,exist_ok=True)
def run(args,**kw):
 print('RUN',pathlib.Path(str(args[0])).name,flush=True)
 subprocess.run(list(map(str,args)),check=True,**kw)
# Include dependency copyright notices alongside the game's licenses.
licenses=BUILD/'assets/licenses/dependencies'
licenses.mkdir(parents=True,exist_ok=True)
for src in (BUILD/'sources').iterdir():
 if not src.is_dir(): continue
 for f in src.iterdir():
  if f.is_file() and f.name.lower().startswith(('copying','license','copyright','notice')):
   (licenses/src.name).mkdir(exist_ok=True);shutil.copy2(f,licenses/src.name/f.name)
for src in (ROOT.parent/'warzone2100/3rdparty').iterdir():
 if not src.is_dir(): continue
 for f in src.iterdir():
  if f.is_file() and f.name.lower().startswith(('copying','license','copyright','notice')):
   (licenses/('wz-'+src.name)).mkdir(exist_ok=True);shutil.copy2(f,licenses/('wz-'+src.name)/f.name)
shutil.copy2(ROOT/'dependencies.lock.json',BUILD/'assets/licenses/dependencies.lock.json')
shutil.copy2(ROOT/'app/artwork/OCTICONS-LICENSE.txt',BUILD/'assets/licenses/OCTICONS-LICENSE.txt')
# Removed classes must not survive an incremental Java build.
shutil.rmtree(CLASSES); CLASSES.mkdir()
java_sources=sorted((ROOT/'app/src').rglob('*.java'))+sorted((BUILD/'sources/SDL/android-project/app/src/main/java').rglob('*.java'))
# javac's @argfile uses double-quoted paths; pass all sources as an argv list
# instead, so paths containing spaces remain unambiguous.
run([JAVA/'javac','-encoding','UTF-8','-source','8','-target','8','-classpath',JAR,'-d',CLASSES,*java_sources])
run([JAVA/'jar','cf',BUILD/'classes.jar','-C',CLASSES,'.'])
run([BT/'d8','--lib',JAR,'--min-api','26','--output',DEX,BUILD/'classes.jar'],env={**os.environ,'JAVA_HOME':str(JAVA.parent)})
if '--java-only' in sys.argv: print('Java and DEX compilation passed');sys.exit(0)
libs=STAGE/'lib/arm64-v8a';libs.mkdir(parents=True,exist_ok=True)
inputs={
 'libwarzone2100.so':BUILD/'engine/src/libwarzone2100.so',
 'libSDL3.so':BUILD/'prefix/lib/libSDL3.so',
 'libc++_shared.so':NDK/'toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so'
}
for name,path in inputs.items():
 if not path.is_file(): raise SystemExit('Missing native library: '+str(path))
 shutil.copy2(path,libs/name);run([LLVM/'llvm-strip','--strip-unneeded',libs/name])
 header=subprocess.check_output([str(LLVM/'llvm-readelf'),'-h',str(libs/name)],text=True)
 if 'AArch64' not in header: raise SystemExit('Not ARM64: '+name)
 dynamic=subprocess.check_output([str(LLVM/'llvm-readelf'),'-d',str(libs/name)],text=True)
 needed=re.findall(r'Shared library: \[(.*?)\]',dynamic)
 system={'libc.so','libm.so','libdl.so','liblog.so','libandroid.so','libEGL.so','libGLESv1_CM.so','libGLESv2.so','libGLESv3.so','libOpenSLES.so','libaaudio.so','libz.so','libvulkan.so'}
 if set(needed)-set(inputs)-system: raise SystemExit('Unbundled libraries: '+repr(needed))
 print(name,'needs',needed,flush=True)
symbols=subprocess.check_output([str(LLVM/'llvm-nm'),'-D','--defined-only',str(libs/'libwarzone2100.so')],text=True)
for symbol in ('SDL_main','Java_org_warzone2100_android_GameActivity_nativePauseAudio','libintl_gettext','libintl_dgettext','libintl_ngettext'):
 if not re.search(r'\b'+symbol+r'$',symbols,re.M): raise SystemExit('Missing native entry point: '+symbol)
run([sys.executable,ROOT/'scripts/prepare-revision.py','--verify-build'])
config=(BUILD/'engine/wz2100-generated-config.h').read_text()
if not re.search(r'^#define ENABLE_NLS 1$',config,re.M): raise SystemExit('Native language support is disabled')
app_manifest=ET.parse(ROOT/'app/AndroidManifest.xml').getroot()
android_ns='{http://schemas.android.com/apk/res/android}'
net_header=(BUILD/'engine/lib/netplay/netplay_config.h').read_text()
build_info={
 'version_name':app_manifest.attrib[android_ns+'versionName'],
 'version_code':int(app_manifest.attrib[android_ns+'versionCode']),
 'source_commit':subprocess.check_output(['git','-C',str(ROOT.parent/'warzone2100'),'rev-parse','HEAD'],text=True).strip(),
 'network_protocol':[int(re.search(r'NETCODE_VERSION_'+part+r'\s*=\s*(\w+)',net_header)[1],0) for part in ('MAJOR','MINOR')],
 'native_language_support':True,
 'engine_sha256':hashlib.file_digest((libs/'libwarzone2100.so').open('rb'),'sha256').hexdigest()
}
(BUILD/'assets/build-info.json').write_text(json.dumps(build_info,indent=2)+'\n')
run([BT/'aapt','package','-f','-M',ROOT/'app/AndroidManifest.xml','-I',JAR,'-S',ROOT/'app/res','-A',BUILD/'assets','-0','wz','-0','opus','-F',BUILD/'resources.ap_'])
unsigned=BUILD/'unsigned.apk';shutil.copy2(BUILD/'resources.ap_',unsigned)
with zipfile.ZipFile(unsigned,'a') as z:
 z.write(DEX/'classes.dex','classes.dex',compress_type=zipfile.ZIP_DEFLATED)
 for lib in sorted(libs.iterdir()): z.write(lib,'lib/arm64-v8a/'+lib.name,compress_type=zipfile.ZIP_STORED)
# Installation extracts native libraries. Align the APK too, for 16 KB devices.
run([BT/'zipalign','-P','16','-f','4',unsigned,BUILD/'aligned.apk'])
key=ROOT/'local-debug.keystore'
if not key.exists():
 run([JAVA/'keytool','-genkeypair','-keystore',key,'-storepass','android','-keypass','android','-alias','androiddebugkey','-keyalg','RSA','-keysize','2048','-validity','10000','-dname','CN=Warzone Local Android Build,O=Local,C=ID'])
 key.chmod(0o600)
output=ROOT.parent/'Warzone2100-4.7.0-android-arm64.apk'
run([BT/'apksigner','sign','--ks',key,'--ks-pass','pass:android','--key-pass','pass:android','--ks-key-alias','androiddebugkey','--out',output,BUILD/'aligned.apk'],env={**os.environ,'JAVA_HOME':str(JAVA.parent)})
run([BT/'apksigner','verify','--verbose',output],env={**os.environ,'JAVA_HOME':str(JAVA.parent)})
run([BT/'zipalign','-c','-P','16','4',output])
with output.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
output.with_suffix('.apk.sha256').write_text(digest+'  '+output.name+'\n')
print('APK:',output,'bytes:',output.stat().st_size,'SHA256:',digest,flush=True)
