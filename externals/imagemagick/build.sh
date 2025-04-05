#!/bin/bash

set -e

rm -rf build
# Can't run it without libfuse (which may not be available), but we can extract it and then run.
./magick --appimage-extract
mv squashfs-root build
(
    cd build ;
    ln -s ./AppRun ./magick
)
