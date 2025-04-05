#!/bin/bash

set -e

# Prepare externals.
(
    cd ./externals/exiftool ;
    ./build.sh
)

# Add externals to PATH.
export PATH="$PATH:$(pwd)/externals/exiftool/build"
export PATH="$PATH:$(pwd)/externals/build"

# Build the website.
(
    python3.11 -m venv .deployvenv ;
    source .deployvenv/bin/activate ;
    pip install --upgrade pip ;
    cd ./source ;
    pip install -r requirements.txt ;
    python -m buildtool --verbose
)
