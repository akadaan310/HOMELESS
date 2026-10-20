#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p artifacts/runtime
g++ -std=c++17 -O2 -static runtime/native/darkctl.cpp -o artifacts/runtime/darkctl
python3 -m unittest discover -s tests -p test_workers.py -v
