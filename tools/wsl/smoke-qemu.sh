#!/usr/bin/env bash
# Firmware-free smoke test for the custom idemu-shm PCI device.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
QEMU="$ROOT/bin/qemu-system-x86_64"
NAME="/idemu-smoke-$$"
FILE="/dev/shm/${NAME#/}"
PIDFILE="/tmp/idemu-qemu-smoke-$$.pid"

cleanup() {
  if [[ -f "$PIDFILE" ]]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null || true
    for _ in {1..100}; do kill -0 "$(cat "$PIDFILE")" 2>/dev/null || break; sleep 0.02; done
  fi
  rm -f "$PIDFILE"
}
trap cleanup EXIT

[[ -x "$QEMU" ]] || { echo "Custom QEMU missing: $QEMU" >&2; exit 2; }
"$QEMU" -L "$ROOT/bin/qemu-share" -M q35 -nodefaults -display none -monitor none -serial none -S \
  -device "idemu-shm,shm-name=$NAME,size=4M" -daemonize -pidfile "$PIDFILE"
for _ in {1..100}; do [[ -f "$FILE" ]] && break; sleep 0.02; done
[[ -f "$FILE" ]] || { echo "Shared-memory object was not created" >&2; exit 1; }
python3 - "$FILE" <<'PY'
import mmap, os, sys
path = sys.argv[1]
assert os.path.getsize(path) == 4 << 20
with open(path, 'r+b', buffering=0) as f:
    with mmap.mmap(f.fileno(), 4096) as m:
        m[:12] = b'IDEMU-SMOKE\0'
        assert m[:12] == b'IDEMU-SMOKE\0'
PY
kill "$(cat "$PIDFILE")"
for _ in {1..100}; do [[ ! -e "$FILE" ]] && break; sleep 0.02; done
[[ ! -e "$FILE" ]] || { echo "Shared-memory object was not cleaned up" >&2; exit 1; }
echo "idemu-shm create/map/cleanup: ok"
