# iDrive 7 on Windows through WSL2

The Windows browser is the UI; Python, QEMU, the renderer and all generated images run inside Ubuntu WSL2. Keep the checkout and PSdZData in the Linux filesystem (`~/...`), not under `/mnt/c` or OneDrive.

## Port status and handoff (2026-11-17)

The firmware-independent host port is implemented and verified on Windows 11 x64 with Ubuntu 26.04 WSL2:

- the checkout is on WSL ext4 at `/home/towab/src/IDEmuEx`;
- `glhost7` builds with headless EGL/OpenGL Core while the macOS CGL path remains intact;
- `/dev/dxg` selects Mesa D3D12 and reports `D3D12 (Intel(R) UHD Graphics)`; llvmpipe remains the fallback;
- QEMU 11.1.2 builds with the `idemu-shm` PCI device and the SDHCI snapshot fix;
- the synthetic renderer test creates a valid 64 x 32 `frame.rgba`;
- `tools/wsl/smoke-qemu.sh` verifies shared-memory creation, mapping and the runtime cleanup path;
- the Windows launcher starts the WSL backend and waits for `/api/state` before opening the browser.

The real HU milestone is **not yet verified**. No `full.7z` or PSdZData was present during this work, and `doctor` reported 0/19 required packages. Consequently, image construction, a 1920 x 720 cold boot, live frames, input, guest logs and snapshot restore have not been tested on WSL. Do not describe the WSL port as a working iDrive VM until those checks pass.

## Setup

```bash
git clone <your fork URL> ~/src/IDEmuEx
cd ~/src/IDEmuEx
tools/wsl/bootstrap.sh
src/mgu/build_host.sh
tools/wsl/build-qemu.sh ~/Downloads/qemu-11.1.2.tar.xz
tools/wsl/smoke-qemu.sh
python3 -m idemu doctor --target id7 --psdz /path/to/psdzdata
```

`doctor` must find all 19 exact packages before the firmware build is attempted. It never modifies the PSdZData. Add `--hash --json` to create a local inventory; do not commit that report or any BMW files.

The exact gate is application IDs `566c`, `566d`, `566e`, `566f`, `5670`, `5671`, `5672`, `5673`, `5675`, `5678`, `567a` and data IDs `566b`, `567b`, `567c`, `567d`, `567e`, `5682`, `5683`, all at `030_016_002`, plus `swfl_00005684.bin.036_010_004`. Use `7z l full.7z` to list an archive without running anything from it. Extract only data you are legally entitled to use, keep it outside Git, and point `doctor --psdz` at the directory containing `swe/swfl` (or its parent PSdZData tree).

Start the interface with `python3 -m idemu gui --no-browser`, then open <http://127.0.0.1:8765/> in Windows. To install a Windows launcher, run this in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File tools\wsl\install-launcher.ps1 -WslRepoPath /home/YOU/src/IDEmuEx
```

## Performance and troubleshooting

The supported path uses `bin/qemu-system-x86_64` with `idemu-shm`; the distro QEMU serial fallback is diagnostic-only and is roughly 100 times slower for graphics. `doctor` reports whether snapshots are available.

On WSL2, `/dev/dxg` should exist and `glhost7 --probe` should name an accelerated renderer. `llvmpipe`, `softpipe` or `swrast` work as fallbacks but are slow. Update the Windows GPU driver and WSL (`wsl --update`) when `/dev/dxg` is missing.

The first HU boot may take several minutes. Fast boot becomes available only after a successful cold boot settles and QEMU saves a snapshot. A stale or invalid snapshot is discarded automatically and retried as a cold boot.

Known issues discovered during the port:

- QEMU 11.1.2 needs `python3-venv` to create its Meson environment. The bootstrap script installs it.
- A minimal QEMU configuration needs `--enable-tools`, otherwise Ninja has no `qemu-img` target. The build script already includes it.
- Mesa may choose llvmpipe even when `/dev/dxg` exists. `idemu.hostcaps.renderer_environment()` probes `GALLIUM_DRIVER=d3d12`; the runtime uses it only when the probe succeeds, preserving software fallback and explicit user overrides.
- QEMU process exit does not reliably unlink its POSIX shared-memory object. `Mgu7Runtime._kill_children()` explicitly calls `shm_unlink`; keep that cleanup even if QEMU shutdown behavior changes.
- Windows Desktop folders may be redirected into OneDrive. The launcher installer uses Windows' registered Desktop location rather than assuming `%USERPROFILE%\Desktop`.
- A checkout under `/mnt/c` may work for source inspection but is unsuitable for extraction, multi-gigabyte images, qcow2 overlays and snapshots.

## Continuation checklist

1. Run `7z l full.7z` and `python3 -m idemu doctor --target id7 --psdz <path> --hash --json`; retain the inventory locally, never in Git.
2. Stop if any of the 19 filenames or versions is missing or different. The binary patches are version-specific.
3. Run the complete non-firmware test suite and `src/mgu/build_host.sh`, `bin/glhost7 --selftest <temp-dir>`, and `tools/wsl/smoke-qemu.sh`.
4. Build one HU environment and perform a cold boot before investigating fast boot. Record the console, renderer and QEMU logs outside Git.
5. Verify 1920 x 720 output, continuing frame updates, touch, rotor, MENU/BACK/OPTION, guest logs and clean stop/restart.
6. Only after cold boot is stable, verify qcow2/GL replay restore under 30 seconds and corrupt-snapshot fallback.

Firmware, extracted trees, `mgu7/`, environments, logs, hashes and snapshots must remain ignored and must never be pushed.
