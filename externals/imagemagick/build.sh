#!/bin/bash

set -e

# Can't run it without libfuse (which may not be available), but we can extract it and then run.
./magick --appimage-extract
mv squashfs-root build
ln -s build/AppRun build/magick
