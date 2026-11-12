#!/usr/bin/env python3
"""Keep release network versioning correct even with a shallow source checkout.

Upstream derives the release protocol minor from the chronological position of
its annotated Git tag. A --depth 1 --branch clone only has one tag and silently
generates protocol 1, hiding every official 4.7.0 host (protocol 104).
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'warzone2100'
RELEASE = '4.7.0'
COMMIT = '7d3d8e51a61ceee89e6bf672a41337e1a9cd7392'
PROTOCOL = (0x4000, 104)

def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args], text=True).strip()

def release_tag_index():
    tags = [row[4:] for row in git('for-each-ref', 'refs/tags/',
            '--format=%(objecttype) %(refname:short)', '--sort=taggerdate').splitlines()
            if row.startswith('tag ')]
    return tags.index(RELEASE) + 1 if RELEASE in tags else 0

def main():
    if git('rev-parse', 'HEAD') != COMMIT or git('rev-parse', RELEASE + '^{commit}') != COMMIT:
        raise SystemExit('Source revision differs from bundled 4.7.0 data; update the release inputs together.')

    if release_tag_index() != PROTOCOL[1]:
        if '--verify-build' in sys.argv:
            raise SystemExit('Incomplete release tag metadata.')
        print('Fetching upstream release tag metadata for multiplayer compatibility', flush=True)
        # Fetch only tags/commits, without historical file contents or submodules.
        subprocess.run(['git', '-C', str(SOURCE), 'fetch', '--filter=tree:0', '--depth=1',
                        '--no-recurse-submodules', 'origin', 'refs/tags/*:refs/tags/*'], check=True)
    if release_tag_index() != PROTOCOL[1]:
        raise SystemExit('Unexpected 4.7.0 tag index; refusing to build an incompatible multiplayer APK.')

    if '--verify-build' in sys.argv:
        header = (ROOT / 'build/engine/lib/netplay/netplay_config.h').read_text()
        values = tuple(int(re.search(r'NETCODE_VERSION_' + name + r'\s*=\s*(\w+)', header)[1], 0)
                       for name in ('MAJOR', 'MINOR'))
        if values != PROTOCOL:
            raise SystemExit(f'Wrong built network protocol: {values}; expected {PROTOCOL}')
    print(f'Release {RELEASE}: network protocol {PROTOCOL[0]}/{PROTOCOL[1]} (matches PC)', flush=True)

if __name__ == '__main__':
    main()
