#!/usr/bin/env bash
# Build the iDrive 7 QEMU 11.1.2 host tools on Linux/WSL2.
set -euo pipefail
TAR=${1:?usage: tools/wsl/build-qemu.sh /path/to/qemu-11.1.2.tar.xz}
[[ -f "$TAR" ]] || { echo "QEMU archive not found: $TAR" >&2; exit 2; }
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
WORK=${IDEMU_QEMU_BUILD_DIR:-"$HOME/.cache/idemu-qemu"}
SRC="$WORK/qemu-11.1.2"
mkdir -p "$WORK"
if [[ ! -d "$SRC" ]]; then tar -C "$WORK" -xf "$TAR"; fi
[[ -f "$SRC/VERSION" ]] && grep -qx '11.1.2' "$SRC/VERSION" || { echo "Expected QEMU 11.1.2" >&2; exit 2; }
cp "$ROOT/src/qemu/idemu-shm.c" "$SRC/hw/misc/idemu-shm.c"
cp "$ROOT/src/qemu/sdhci-pci.c" "$SRC/hw/sd/sdhci-pci.c"
python3 - "$SRC" <<'PY'
import pathlib, sys
s = pathlib.Path(sys.argv[1])
p = s / 'hw/misc/Kconfig'; t = p.read_text()
if 'config IDEMU_SHM' not in t:
    t = t.replace('config PCI_TESTDEV\n', 'config IDEMU_SHM\n    bool\n    default y if PCI_DEVICES\n    depends on PCI\n\nconfig PCI_TESTDEV\n', 1); p.write_text(t)
p = s / 'hw/misc/meson.build'; t = p.read_text()
if "CONFIG_IDEMU_SHM" not in t:
    t = t.replace("system_ss.add(when: 'CONFIG_PCI_TESTDEV'", "system_ss.add(when: 'CONFIG_IDEMU_SHM', if_true: files('idemu-shm.c'))\nsystem_ss.add(when: 'CONFIG_PCI_TESTDEV'", 1); p.write_text(t)
PY
mkdir -p "$WORK/build"
cd "$WORK/build"
if [[ ! -f build.ninja ]]; then
  "$SRC/configure" --target-list=x86_64-softmmu --disable-docs --disable-guest-agent \
    --disable-gtk --disable-sdl --disable-vnc --disable-curses --disable-rust \
    --disable-user --disable-linux-user --disable-bsd-user --without-default-features --enable-tcg
fi
ninja qemu-system-x86_64 qemu-img
mkdir -p "$ROOT/bin/qemu-share"
install -m755 qemu-system-x86_64 "$ROOT/bin/qemu-system-x86_64"
install -m755 qemu-img "$ROOT/bin/qemu-img"
for f in bios-256k.bin vgabios-stdvga.bin linuxboot_dma.bin kvmvapic.bin; do cp "$SRC/pc-bios/$f" "$ROOT/bin/qemu-share/"; done
"$ROOT/bin/qemu-system-x86_64" -device help 2>&1 | grep -q idemu-shm
echo "Built QEMU with idemu-shm and qemu-img in $ROOT/bin"
