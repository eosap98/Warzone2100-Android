#!/usr/bin/env python3
"""Read the real PC lobby and compare its hosts with the built network version.

This is a host-side HTTP/compatibility check, not a phone or multiplayer match test.
"""
import datetime
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'warzone2100'
header = (ROOT / 'build/engine/lib/netplay/netplay_config.h').read_text()
protocol = [int(re.search(r'NETCODE_VERSION_' + name + r'\s*=\s*(\w+)', header)[1], 0)
            for name in ('MAJOR', 'MINOR')]
assert protocol == [16384, 104], f'Wrong protocol: {protocol}'

# Use the endpoint shipped by upstream, including its path prefix.
lobby_source = (SOURCE / 'lib/netplay/netlobby.h').read_text()
encoded = re.search(r'lobbyAddressEncoded\s*=\s*\{(.*?)\}', lobby_source, re.S)[1]
key = int(re.search(r'scr_key\s*=\s*(0x[0-9A-Fa-f]+)', lobby_source)[1], 0)
base_url = ''.join(chr(int(value, 16) ^ key) for value in re.findall(r'0x[0-9A-Fa-f]+', encoded))
response = subprocess.check_output([
    'curl', '--fail', '--silent', '--show-error', '--noproxy', '*', '--max-time', '30',
    '-H', 'Origin: wz2100://wz2100.net',
    '-H', 'Referer: https://github.com/Warzone2100/warzone2100?wz_internal=list',
    '-H', 'Accept: application/jsonl',
    '-A', 'Warzone2100/4.7.0 (+https://github.com/Warzone2100/warzone2100)',
    base_url + '/api/v1/games'
], text=True)
rows = [json.loads(line) for line in response.splitlines() if line.strip()]
assert any(row.get('type') == 'header' for row in rows), 'Missing lobby header'
games = [row for row in rows if 'id' in row]
compatible = [game for game in games if game['netv'] == protocol]
tcp_hosts = [game for game in compatible if any(conn.split(':')[0] == 'tcp' for conn in game['conn'])]
report = {
    'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Host HTTPS query and compiled protocol; no emulator or game join',
    'http_status': 200,
    'network_protocol': protocol,
    'hosts_returned': len(games),
    'compatible_hosts': len(compatible),
    'compatible_tcp_hosts': len(tcp_hosts),
    'old_build_compatible_hosts': sum(game['netv'] == [16384, 1] for game in games),
}
(ROOT / 'lobby-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
