#!/bin/sh
set -ex
rm -rf bin develop-eggs eggs include lib parts
python3 -m venv .
bin/pip install zc.buildout
bin/buildout
