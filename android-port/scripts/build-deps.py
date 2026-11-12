#!/usr/bin/env python3
"""Pinned ARM64 Android dependencies. No host binaries enter the APK."""
import concurrent.futures, hashlib, json, os, pathlib, shutil, subprocess, sys, tarfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
SDK = pathlib.Path(os.environ.get('ANDROID_HOME', str(pathlib.Path.home()/'Android/Sdk')))
NDK = pathlib.Path(os.environ.get('ANDROID_NDK_HOME', str(SDK/'ndk/27.2.12479018')))
CMAKE = str(ROOT/'build/host-tools/cmake/data/bin/cmake')
NINJA = str(SDK/'cmake/3.22.1/bin/ninja')
PREFIX = ROOT/'build/prefix'
SOURCES = ROOT/'build/sources'
DOWNLOADS = ROOT/'build/downloads'
JOBS = os.environ.get('JOBS', '3')
DEPS = [
 ('iconv','https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.17.tar.gz','iconv'),
 ('gettext','https://ftp.gnu.org/pub/gnu/gettext/gettext-0.22.5.tar.xz','gettext'),
 ('zlib','https://zlib.net/fossils/zlib-1.3.1.tar.gz', ['ZLIB_BUILD_EXAMPLES=OFF']),
 ('ogg','https://downloads.xiph.org/releases/ogg/libogg-1.3.5.tar.xz', ['INSTALL_DOCS=OFF']),
 ('vorbis','https://downloads.xiph.org/releases/vorbis/libvorbis-1.3.7.tar.xz', []),
 ('theora','https://downloads.xiph.org/releases/theora/libtheora-1.1.1.tar.xz', 'theora'),
 ('opus','https://downloads.xiph.org/releases/opus/opus-1.5.2.tar.gz', ['OPUS_BUILD_TESTING=OFF','OPUS_BUILD_PROGRAMS=OFF']),
 ('sodium','https://download.libsodium.org/libsodium/releases/libsodium-1.0.20.tar.gz','autotools'),
 ('sqlite','https://www.sqlite.org/2025/sqlite-autoconf-3500400.tar.gz','sqlite'),
 ('SDL','https://github.com/libsdl-org/SDL/releases/download/release-3.2.20/SDL3-3.2.20.tar.gz', ['SDL_SHARED=ON','SDL_STATIC=OFF','SDL_TESTS=OFF','SDL_TEST_LIBRARY=OFF','SDL_EXAMPLES=OFF']),
 ('physfs','https://github.com/icculus/physfs/archive/refs/tags/release-3.2.0.tar.gz', ['PHYSFS_BUILD_SHARED=OFF','PHYSFS_BUILD_TEST=OFF','PHYSFS_BUILD_DOCS=OFF']),
 ('png','https://github.com/pnggroup/libpng/archive/refs/tags/v1.6.50.tar.gz', ['PNG_SHARED=OFF','PNG_TESTS=OFF','PNG_TOOLS=OFF']),
 ('freetype','https://download.savannah.gnu.org/releases/freetype/freetype-2.13.3.tar.xz', ['FT_DISABLE_HARFBUZZ=ON','FT_DISABLE_BZIP2=ON','FT_DISABLE_BROTLI=ON','FT_DISABLE_PNG=ON']),
 ('harfbuzz','https://github.com/harfbuzz/harfbuzz/archive/refs/tags/8.5.0.tar.gz', ['HB_BUILD_UTILS=OFF','HB_BUILD_TESTS=OFF','HB_HAVE_FREETYPE=ON','HB_HAVE_GLIB=OFF','HB_HAVE_ICU=OFF']),
 ('jpeg','https://github.com/libjpeg-turbo/libjpeg-turbo/releases/download/3.1.1/libjpeg-turbo-3.1.1.tar.gz', ['ENABLE_SHARED=OFF','WITH_TESTS=OFF','WITH_TOOLS=OFF']),
 ('openal','https://github.com/kcat/openal-soft/archive/refs/tags/1.24.3.tar.gz', ['LIBTYPE=STATIC','ALSOFT_UTILS=OFF','ALSOFT_EXAMPLES=OFF','ALSOFT_TESTS=OFF','ALSOFT_INSTALL_CONFIG=OFF','ALSOFT_INSTALL_HRTF_DATA=OFF','ALSOFT_INSTALL_AMBDEC_PRESETS=OFF','ALSOFT_BACKEND_OPENSL=ON','ALSOFT_BACKEND_OBOE=OFF']),
 ('mbedtls','https://github.com/Mbed-TLS/mbedtls/archive/refs/tags/v2.28.10.tar.gz', ['ENABLE_TESTING=OFF','ENABLE_PROGRAMS=OFF','USE_SHARED_MBEDTLS_LIBRARY=OFF']),
 ('curl','https://curl.se/download/curl-8.14.1.tar.xz', ['BUILD_CURL_EXE=OFF','BUILD_TESTING=OFF','CURL_USE_OPENSSL=OFF','CURL_USE_MBEDTLS=ON','CURL_USE_LIBPSL=OFF','CURL_USE_LIBSSH2=OFF','CURL_BROTLI=OFF','CURL_ZSTD=OFF','CURL_DISABLE_LDAP=ON','CURL_DISABLE_LDAPS=ON','CURL_CA_PATH=/system/etc/security/cacerts','HTTP_ONLY=ON']),
 ('zip','https://libzip.org/download/libzip-1.11.4.tar.xz', ['ENABLE_COMMONCRYPTO=OFF','ENABLE_GNUTLS=OFF','ENABLE_MBEDTLS=OFF','ENABLE_OPENSSL=OFF','ENABLE_BZIP2=OFF','ENABLE_LZMA=OFF','ENABLE_ZSTD=OFF','BUILD_TOOLS=OFF','BUILD_REGRESS=OFF','BUILD_EXAMPLES=OFF','BUILD_DOC=OFF']),
]
for d in (PREFIX,SOURCES,DOWNLOADS,ROOT/'build/logs'): d.mkdir(parents=True,exist_ok=True)
env = dict(os.environ)
BIN = NDK/'toolchains/llvm/prebuilt/linux-x86_64/bin'
env.update(CC=str(BIN/'aarch64-linux-android26-clang'), CXX=str(BIN/'aarch64-linux-android26-clang++'), AR=str(BIN/'llvm-ar'), RANLIB=str(BIN/'llvm-ranlib'), STRIP=str(BIN/'llvm-strip'), CFLAGS='-O2 -fPIC', CXXFLAGS='-O2 -fPIC', LDFLAGS='-Wl,-z,max-page-size=16384', PKG_CONFIG_LIBDIR=str(PREFIX/'lib/pkgconfig'), PKG_CONFIG_PATH=str(PREFIX/'lib/pkgconfig'))
env['PATH'] = str(BIN)+':'+env['PATH']
LOCK = {item['name']: item for item in json.loads((ROOT/'dependencies.lock.json').read_text())}
def download(dep):
 name,url,_=dep; dest=DOWNLOADS/(name+'-'+url.rsplit('/',1)[-1]); src=SOURCES/name
 if not dest.exists():
  print('DOWNLOAD',name,flush=True)
  subprocess.run(['curl','-L','--fail','--retry','3','--connect-timeout','25','-sS',url,'-o',str(dest)+'.part'],check=True)
  pathlib.Path(str(dest)+'.part').replace(dest)
 digest=hashlib.sha256(dest.read_bytes()).hexdigest()
 if LOCK[name]['url'] != url or LOCK[name]['sha256'] != digest:
  raise RuntimeError('Dependency checksum mismatch: '+name)
 if not src.exists():
  tmp=SOURCES/(name+'.extract'); tmp.mkdir(exist_ok=True)
  with tarfile.open(dest) as t: t.extractall(tmp,filter='data')
  dirs=list(tmp.iterdir()); assert len(dirs)==1, dirs
  dirs[0].rename(src); tmp.rmdir()
 return {'name':name,'url':url,'sha256':digest}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 manifest=list(pool.map(download,DEPS))
(ROOT/'build/dependencies.lock.json').write_text(json.dumps(manifest,indent=2)+'\n')
for name,url,opts in DEPS:
 stamp=PREFIX/('.'+name+'-installed')
 if stamp.exists(): print('CACHED',name,flush=True); continue
 print('BUILD',name,flush=True)
 src=SOURCES/name; build=ROOT/'build/deps'/name; build.mkdir(parents=True,exist_ok=True)
 log=open(ROOT/'build/logs'/(name+'.log'),'w')
 def run(args,cwd=build):
  p=subprocess.run(list(map(str,args)),cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT)
  if p.returncode:
   log.flush(); print((ROOT/'build/logs'/(name+'.log')).read_text()[-12000:]);sys.exit(p.returncode)
 if opts=='theora':
  names='apiwrapper bitpack decapiwrapper decinfo decode dequant fragment huffdec idct info internal quant state'.split()
  for n in names:
   run([env['CC'],'-O2','-fPIC','-I'+str(src/'include'),'-I'+str(PREFIX/'include'),'-c',src/'lib'/(n+'.c'),'-o',build/(n+'.o')])
  run([env['AR'],'rcs',PREFIX/'lib/libtheoradec.a',*[build/(n+'.o') for n in names]])
  shutil.copytree(src/'include/theora',PREFIX/'include/theora',dirs_exist_ok=True)
 elif opts in ('autotools', 'iconv', 'gettext'):
  # Legacy libtool does not support whitespace in paths. Use a stable alias
  # for sources/install and a temporary directory for its makefiles.
  alias=pathlib.Path('/tmp') / ('wz2100-deps-' + str(os.getuid()) + '-' + hashlib.sha256(str((ROOT/'build').resolve()).encode()).hexdigest()[:16])
  if not alias.exists(): alias.symlink_to(ROOT/'build',target_is_directory=True)
  assert alias.resolve()==(ROOT/'build').resolve(), 'Build alias belongs to a different project'
  src=alias/'sources'/name
  import tempfile
  build=pathlib.Path(tempfile.mkdtemp(prefix='wz2100-'+name+'-'))
  def run(args,cwd=None):
   p=subprocess.run(list(map(str,args)),cwd=cwd or build,env=env,stdout=log,stderr=subprocess.STDOUT)
   if p.returncode:
    log.flush(); print((ROOT/'build/logs'/(name+'.log')).read_text()[-12000:]);sys.exit(p.returncode)

  configure=src/'configure'
  extra=['--disable-pie'] if opts=='autotools' else []
  if opts=='gettext':
   configure=src/'gettext-runtime/configure'
   extra=['--disable-java','--disable-libasprintf','--with-included-gettext',f'--with-libiconv-prefix={alias}/prefix','--disable-rpath']
  run([configure,'--host=aarch64-linux-android',f'--prefix={alias}/prefix','--disable-shared','--enable-static',*extra])
  run(['make','-j'+JOBS]);run(['make','install']);shutil.rmtree(build)
 elif opts=='sqlite':
  run([env['CC'],'-O2','-fPIC','-DSQLITE_THREADSAFE=1','-DSQLITE_ENABLE_COLUMN_METADATA','-c',src/'sqlite3.c','-o',build/'sqlite3.o'])
  run([env['AR'],'rcs',PREFIX/'lib/libsqlite3.a',build/'sqlite3.o'])
  for h in ('sqlite3.h','sqlite3ext.h'): shutil.copy2(src/h,PREFIX/'include'/h)
 else:
  run([CMAKE,'-S',src,'-B',build,'-G','Ninja',f'-DCMAKE_MAKE_PROGRAM={NINJA}',f'-DCMAKE_TOOLCHAIN_FILE={NDK}/build/cmake/android.toolchain.cmake','-DANDROID_ABI=arm64-v8a','-DANDROID_PLATFORM=android-26','-DANDROID_STL=c++_shared','-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DBUILD_SHARED_LIBS=OFF',f'-DCMAKE_INSTALL_PREFIX={PREFIX}',f'-DCMAKE_PREFIX_PATH={PREFIX}',f'-DCMAKE_FIND_ROOT_PATH={PREFIX}','-DCMAKE_INSTALL_LIBDIR=lib',f'-DZLIB_LIBRARY_RELEASE={PREFIX}/lib/libz.a',f'-DZLIB_LIBRARY_DEBUG={PREFIX}/lib/libz.a','-DCMAKE_POLICY_VERSION_MINIMUM=3.5',*['-D'+s for s in opts]])
  run([CMAKE,'--build',build,'-j',JOBS]);run([CMAKE,'--install',build])
 stamp.touch();log.close();print('INSTALLED',name,flush=True)
print('All Android dependencies installed:',PREFIX,flush=True)
