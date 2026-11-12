#!/usr/bin/env python3
"""Build the same gettext runtime for host tests; never package these host binaries.

Recent glibc treats C.UTF-8 differently from libintl 0.22.5, so using the host's
implicit gettext would test a different implementation from the Android APK.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
PREFIX = BUILD / 'host-gettext'
stamp = PREFIX / '.installed-0.22.5'
if stamp.exists() and (PREFIX / 'lib/libintl.a').is_file():
    print('CACHED host GNU gettext 0.22.5', flush=True)
    raise SystemExit(0)

lock = next(item for item in json.loads((ROOT / 'dependencies.lock.json').read_text()) if item['name'] == 'gettext')
archive = BUILD / 'downloads/gettext-gettext-0.22.5.tar.xz'
assert hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest() == lock['sha256']
alias = pathlib.Path('/tmp') / ('wz2100-deps-' + str(os.getuid()) + '-' + hashlib.sha256(str((ROOT/'build').resolve()).encode()).hexdigest()[:16])
if not alias.exists():
    alias.symlink_to(BUILD, target_is_directory=True)
assert alias.resolve() == BUILD.resolve()
source = alias / 'sources/gettext/gettext-runtime'
assert (source / 'configure').is_file(), 'Run build-deps.py first'
env = dict(os.environ, CC='gcc', CXX='g++', AR='ar', RANLIB='ranlib', STRIP='strip',
           CFLAGS='-O2 -fPIC', CXXFLAGS='-O2 -fPIC', CPPFLAGS='', LDFLAGS='',
           PKG_CONFIG_LIBDIR='', PKG_CONFIG_PATH='')
(BUILD / 'logs').mkdir(parents=True, exist_ok=True)
print('BUILD host GNU gettext 0.22.5 for language tests', flush=True)
with tempfile.TemporaryDirectory(prefix='wz-gettext-host-') as workdir, (BUILD / 'logs/host-gettext.log').open('w') as log:
    def run(args):
        result = subprocess.run(list(map(str, args)), cwd=workdir, env=env, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            log.flush()
            print((BUILD / 'logs/host-gettext.log').read_text()[-10000:])
            raise SystemExit(result.returncode)
    run([source / 'configure', '--prefix=' + str(alias / 'host-gettext'),
         '--disable-shared', '--enable-static', '--with-included-gettext',
         '--disable-java', '--disable-libasprintf', '--disable-rpath'])
    run(['make', '-C', 'intl', '-j' + os.environ.get('JOBS', '3')])
    run(['make', '-C', 'intl', 'install'])
stamp.touch()
print('INSTALLED host GNU gettext 0.22.5', flush=True)
