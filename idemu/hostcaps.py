"""Host/runtime capability detection shared by the API and ``idemu doctor``."""
import functools, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_wsl():
    if sys.platform != 'linux': return False
    if os.environ.get('WSL_DISTRO_NAME') or os.environ.get('WSL_INTEROP'): return True
    try:
        with open('/proc/sys/kernel/osrelease', encoding='ascii') as f:
            return 'microsoft' in f.read().lower()
    except OSError:
        return False


def backend():
    if sys.platform == 'win32': return 'windows-ui-only'
    if sys.platform == 'darwin': return 'macos'
    if is_wsl(): return 'wsl2'
    return 'linux'


def _probe_renderer(path):
    if not os.path.isfile(path): return {'available': False, 'name': None, 'accelerated': False, 'detail': 'bin/glhost7 missing'}
    try:
        r = subprocess.run([path, '--probe'], capture_output=True, text=True, timeout=15)
        detail = (r.stderr or r.stdout).strip().splitlines()
        line = next((x for x in detail if x.startswith('glhost7: ') and ' | ' in x), '')
        name = line[len('glhost7: '):].split(' | ', 1)[0] if line else None
        software = bool(name and any(x in name.lower() for x in ('llvmpipe', 'softpipe', 'swrast')))
        return {'available': r.returncode == 0, 'name': name, 'accelerated': r.returncode == 0 and not software,
                'detail': '\n'.join(detail[-3:]) or ('exit %d' % r.returncode)}
    except (OSError, subprocess.SubprocessError) as e:
        return {'available': False, 'name': None, 'accelerated': False, 'detail': str(e)}


def _probe_qemu(path):
    if not path or not os.path.isfile(path): return {'available': False, 'path': path, 'idemu_shm': False}
    try:
        r = subprocess.run([path, '-device', 'help'], capture_output=True, text=True, timeout=15)
        return {'available': r.returncode == 0, 'path': path, 'idemu_shm': 'idemu-shm' in (r.stdout + r.stderr)}
    except (OSError, subprocess.SubprocessError):
        return {'available': False, 'path': path, 'idemu_shm': False}


@functools.lru_cache(maxsize=1)
def capabilities():
    b = backend(); renderer = _probe_renderer(os.path.join(ROOT, 'bin', 'glhost7'))
    own_qemu = os.path.join(ROOT, 'bin', 'qemu-system-x86_64')
    qemu = _probe_qemu(own_qemu if os.path.isfile(own_qemu) else shutil.which('qemu-system-x86_64'))
    qimg = os.path.join(ROOT, 'bin', 'qemu-img')
    qimg = qimg if os.path.isfile(qimg) else shutil.which('qemu-img')
    vm = b != 'windows-ui-only'
    return {'vm': vm, 'host': sys.platform, 'backend': b, 'renderer': renderer,
            'qemu': qemu, 'fast_boot': bool(vm and renderer['available'] and qemu['idemu_shm'] and qimg)}
