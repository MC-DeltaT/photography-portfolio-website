#!/bin/bash

set -e

# Prepare externals.
(
    cd ./externals/exiftool ;
    mkdir build ;
    gunzip -cd Image-ExifTool-13.26.tar.gz | tar -xf - -C build --strip-components=1
)

# Add externals to PATH.
export PATH="$PATH:$(pwd)/externals/exiftool/build"
export PATH="$PATH:$(pwd)/externals/imagemagick"

# Build the website.
(
    cd ./source ;
    python3.11 -m venv .venv ;
    source .venv/bin/activate ;
    pip install --upgrade pip ;
    pip install -r requirements.txt ;
    python -m buildtool --verbose
)
