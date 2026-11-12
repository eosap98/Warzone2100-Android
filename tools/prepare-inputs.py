#!/usr/bin/env python3
"""Restore pinned upstream inputs separately from the public port repository."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'inputs.lock.json').read_text())
SOURCE = ROOT / 'warzone2100'
PATCH = ROOT / 'android-port/warzone2100-android.patch'


def run(*args):
    subprocess.run(list(map(str, args)), check=True)


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args], text=True).strip()


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check_source():
    if not (SOURCE / '.git').exists():
        raise SystemExit('Source belum tersedia. Jalankan: bash setup.sh')
    if git('rev-parse', 'HEAD') != LOCK['source']['commit']:
        raise SystemExit('Commit source tidak cocok dengan inputs.lock.json.')


def check_patch():
    if digest(PATCH) != LOCK['patch_sha256']:
        raise SystemExit('Checksum patch tidak cocok dengan inputs.lock.json.')


def patch_is_applied():
    return subprocess.run(['git', '-C', str(SOURCE), 'apply', '--reverse', '--check', str(PATCH)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verifikasi saja; tanpa unduhan/perubahan')
    parser.add_argument('--source-only', action='store_true', help='Siapkan source saja, tanpa paket data')
    args = parser.parse_args()
    check_patch()
    if not args.check:
        if not SOURCE.exists():
            run('git', 'clone', '--depth', '1', '--branch', LOCK['source']['tag'],
                LOCK['source']['url'], SOURCE)
        check_source()
        if not patch_is_applied():
            run('git', '-C', SOURCE, 'apply', '--check', PATCH)
            run('git', '-C', SOURCE, 'apply', PATCH)
        run('git', '-C', SOURCE, 'submodule', 'update', '--init', '--depth', '1', '--jobs', '3',
            '--', *LOCK['source']['submodules'])
        run(sys.executable, ROOT / 'android-port/scripts/prepare-revision.py')
    check_source()
    if not patch_is_applied():
        raise SystemExit('Patch Android belum lengkap. Jalankan: bash setup.sh')
    for relative, expected in LOCK['source']['submodules'].items():
        actual = subprocess.check_output(['git', '-C', str(SOURCE / relative), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected:
            raise SystemExit('Submodule tidak cocok: ' + relative)
    tags = [row[4:] for row in git('for-each-ref', 'refs/tags/',
            '--format=%(objecttype) %(refname:short)', '--sort=taggerdate').splitlines()
            if row.startswith('tag ')]
    if LOCK['source']['tag'] not in tags or tags.index(LOCK['source']['tag']) + 1 != 104:
        raise SystemExit('Metadata tag protokol multiplayer belum lengkap. Jalankan: bash setup.sh')
    print('OK: source 4.7.0, patch Android, 16 submodule, protokol 16384/104', flush=True)
    if args.source_only:
        return
    item = LOCK['game_data']
    deb = ROOT / item['filename']
    if not deb.exists() and not args.check:
        part = deb.with_suffix(deb.suffix + '.part')
        run('curl', '-L', '--fail', '--retry', '3', '--connect-timeout', '25', item['url'], '-o', part)
        if digest(part) != item['sha256']:
            raise SystemExit('Checksum data unduhan tidak cocok; file .part tidak digunakan.')
        part.replace(deb)
    if not deb.is_file():
        raise SystemExit('Data game belum tersedia. Jalankan: bash setup.sh')
    if digest(deb) != item['sha256']:
        raise SystemExit('Checksum paket data tidak cocok. Periksa inputs.lock.json.')
    print('OK: paket data resmi 4.7.0, SHA-256 cocok', flush=True)


if __name__ == '__main__':
    main()
