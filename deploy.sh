#!/bin/bash

set -e

# Prepare externals.
(
    cd ./externals/exiftool ;
    ./build.sh
)
(
    cd ./externals/imagemagick ;
    ./build.sh
)

# Add externals to PATH.
export PATH="$PATH:$(pwd)/externals/exiftool/build"
export PATH="$PATH:$(pwd)/externals/imagemagick/build"

# Verify externals are available.
exiftool --version
magick --version

# Build the website.
(
    python3.11 -m venv .deployvenv ;
    . .deployvenv/bin/activate ;
    pip install --upgrade pip ;
    pip install -r requirements.txt ;
    python -m buildtool
)
