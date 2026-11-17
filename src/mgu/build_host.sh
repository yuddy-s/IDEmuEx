#!/usr/bin/env bash
# Build the firmware-independent iDrive 7 host renderer.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ../../bin
if [[ "$(uname -s)" == Darwin ]]; then
  clang -std=gnu11 -O2 -Wno-everything glhost7.c -framework OpenGL -o ../../bin/glhost7
else
  : "${CC:=clang}"
  "$CC" -std=gnu11 -O2 -Wall -Wextra -Wno-unused-parameter glhost7.c \
    -o ../../bin/glhost7 $(pkg-config --cflags --libs egl gl) -lrt
fi
../../bin/glhost7 --probe
