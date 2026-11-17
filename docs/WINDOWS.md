# IDEmuEx on Windows

IDEmuEx is a fork of [IDEmu](https://github.com/herrbimmer/IDEmu). It checks out and starts its web interface on Windows. The original Python package name remains `idemu` so existing tools and data files keep working.

## Run the interface

Install Python 3.10 or later with Tkinter, then double-click `IDEmuEx.cmd` or run:

```powershell
py -3 -m idemu gui
```

Open <http://127.0.0.1:8765/> if your browser does not open automatically. The Electron wrapper is optional; it needs Node.js and `npm install` in `electron/`, followed by `npm start`. Set `IDEMU_PYTHON` to a Python executable if the wrapper cannot find it.

The Windows interface supports package selection, environment setup, file browsing, and parts of the image and coding tooling. A firmware image build has **not** been verified end to end on Windows. Firmware is not included; use packages you are entitled to use.

## VM execution status

**The head-unit VM does not run on native Windows yet.** The interface disables Start and the API returns a clear error. The upstream runtime expects Unix domain sockets, POSIX shared memory and signals, renderers, and custom QEMU devices. iDrive 8 additionally uses Apple's Hypervisor framework and `DYLD_INSERT_LIBRARIES`.

The iDrive 7 host components have a verified Linux/EGL and custom-QEMU backend for WSL2. Follow [the WSL2 guide](WSL2.md); the backend, generated images and firmware packages must live in the Ubuntu filesystem for acceptable performance. The host plumbing is verified, but the real BMW image has not yet been built or cold-booted on WSL because the required firmware was unavailable during the port.

Other generations still need Windows or portable replacements for their renderer, accelerator and host integration. The existing macOS paths are retained.

## Checkout fix

Upstream tracked `tools/cic/con.py`. `CON` is a reserved Windows device name, so Git cannot check that path out on Windows. IDEmuEx renames it to `tools/cic/cic_console.py` and updates the CIC documentation. Clone this fork directly after the rename is committed; cloning the upstream repository directly on Windows still hits the reserved name.

## Run checks

```powershell
py -3 -m idemu list
py -3 -m unittest discover -s tests -p test_windows_host.py
```

The full upstream test suite includes Unix socket, POSIX permission and macOS renderer assumptions. Those tests are not currently a Windows pass gate.
