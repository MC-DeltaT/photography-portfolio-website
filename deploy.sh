#!/bin/bash

# TODO: build needs other packages which we don't have in CI

cd ./source

python3.11 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python -m buildtool --verbose
