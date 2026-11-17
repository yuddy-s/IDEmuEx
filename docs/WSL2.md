# iDrive 7 on Windows through WSL2

The Windows browser is the UI; Python, QEMU, the renderer and all generated images run inside Ubuntu WSL2. Keep the checkout and PSdZData in the Linux filesystem (`~/...`), not under `/mnt/c` or OneDrive.

## Setup

```bash
git clone <your fork URL> ~/src/IDEmuEx
cd ~/src/IDEmuEx
tools/wsl/bootstrap.sh
src/mgu/build_host.sh
tools/wsl/build-qemu.sh ~/Downloads/qemu-11.1.2.tar.xz
python3 -m idemu doctor --target id7 --psdz /path/to/psdzdata
```

`doctor` must find all 19 exact packages before the firmware build is attempted. It never modifies the PSdZData. Add `--hash --json` to create a local inventory; do not commit that report or any BMW files.

Start the interface with `python3 -m idemu gui --no-browser`, then open <http://127.0.0.1:8765/> in Windows. To install a Windows launcher, run this in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File tools\wsl\install-launcher.ps1 -WslRepoPath /home/YOU/src/IDEmuEx
```

## Performance and troubleshooting

The supported path uses `bin/qemu-system-x86_64` with `idemu-shm`; the distro QEMU serial fallback is diagnostic-only and is roughly 100 times slower for graphics. `doctor` reports whether snapshots are available.

On WSL2, `/dev/dxg` should exist and `glhost7 --probe` should name an accelerated renderer. `llvmpipe`, `softpipe` or `swrast` work as fallbacks but are slow. Update the Windows GPU driver and WSL (`wsl --update`) when `/dev/dxg` is missing.

The first HU boot may take several minutes. Fast boot becomes available only after a successful cold boot settles and QEMU saves a snapshot. A stale or invalid snapshot is discarded automatically and retried as a cold boot.
