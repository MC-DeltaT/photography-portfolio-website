#!/bin/bash

set -e

rm -rf build
mkdir -p build
gunzip -cd Image-ExifTool-13.26.tar.gz | tar -xf - -C build --strip-components=1
