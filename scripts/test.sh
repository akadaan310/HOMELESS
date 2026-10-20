#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m pytest tests -q
npm --prefix web test
