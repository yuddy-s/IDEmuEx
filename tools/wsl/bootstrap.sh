#!/usr/bin/env bash
# Install firmware-independent build/runtime dependencies for Ubuntu WSL2.
set -euo pipefail
if ! grep -qi microsoft /proc/sys/kernel/osrelease; then
  echo "This bootstrap is intended for WSL2." >&2; exit 2
fi
sudo apt-get update
sudo apt-get install -y \
  build-essential clang lld git curl xz-utils python3 python3-venv python3-tk \
  ninja-build pkg-config libglib2.0-dev libpixman-1-dev \
  libegl1-mesa-dev libgl-dev mesa-utils
echo "Dependencies installed. Build the renderer with: src/mgu/build_host.sh"
echo "Build QEMU with: tools/wsl/build-qemu.sh /path/to/qemu-11.1.2.tar.xz"
