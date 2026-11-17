"""Firmware-safe host and package diagnostics for IDEmu."""
import hashlib, json, os, platform, shutil, subprocess, sys
from . import catalog, hostcaps, mgu7


def _memory():
    try:
        with open('/proc/meminfo') as f: values = dict(line.split(':', 1) for line in f if ':' in line)
        return int(values['MemTotal'].split()[0]) * 1024
    except (OSError, KeyError, ValueError): return None


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(8 << 20), b''): h.update(block)
    return h.hexdigest()


def report(target='id7', psdz=None, hashes=False):
    if target not in ('id7', 'mgu7'): raise ValueError('only the id7 target is supported')
    caps = hostcaps.capabilities()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    disk = shutil.disk_usage(root)
    tools = {n: shutil.which(n) for n in ('python3', 'git', 'clang', 'ld.lld', 'ninja', 'pkg-config', 'qemu-system-x86_64', 'qemu-img')}
    pkg = catalog.package_status('mgu7', psdz)
    if hashes:
        for item in pkg['items']:
            if item['found']: item['sha256'] = _sha256(item['path'])
    checks = {
        'backend': caps['backend'] == 'wsl2',
        'space': disk.free >= (12 << 30),
        'memory': (_memory() or 0) >= (6 << 30),
        'dxg': not hostcaps.is_wsl() or os.path.exists('/dev/dxg'),
        'renderer': caps['renderer']['available'],
        'qemu': caps['qemu']['available'],
        'idemu_shm': caps['qemu']['idemu_shm'],
        'firmware': pkg['ok'],
    }
    return {'target': 'id7', 'platform': {'system': platform.system(), 'release': platform.release(), 'python': sys.version.split()[0],
            'wsl_distro': os.environ.get('WSL_DISTRO_NAME'), 'memory': _memory(), 'disk_free': disk.free, 'dxg': os.path.exists('/dev/dxg')},
            'capabilities': caps, 'tools': tools, 'packages': pkg, 'checks': checks, 'ready': all(checks.values())}


def print_report(data):
    mark = lambda x: 'OK' if x else 'MISSING'
    print('IDEmu doctor: iDrive 7 / WSL2')
    for key, value in data['checks'].items(): print('  %-12s %s' % (key, mark(value)))
    r = data['capabilities']['renderer']; print('  renderer     %s%s' % (r.get('name') or r.get('detail'), '' if r.get('accelerated') else ' (software/unavailable)'))
    print('  disk free    %.1f GiB' % (data['platform']['disk_free'] / (1 << 30)))
    print('  packages     %d/%d exact files' % (data['packages']['have'], data['packages']['total']))
    for item in data['packages']['items']:
        print('    %s %s%s' % ('OK ' if item['found'] else '---', item['file'], ('  ' + item.get('sha256', '')) if item.get('sha256') else ''))


def main(argv):
    target = argv[argv.index('--target') + 1] if '--target' in argv else 'id7'
    psdz = argv[argv.index('--psdz') + 1] if '--psdz' in argv else None
    data = report(target, psdz, '--hash' in argv)
    if '--json' in argv: print(json.dumps(data, indent=2))
    else: print_report(data)
    return 0 if data['ready'] else 1
