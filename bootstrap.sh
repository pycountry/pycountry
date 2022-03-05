#!/bin/sh
set -ex
version=${1:-3}
rm -rf bin develop-eggs eggs include lib parts
python${version} -m venv .
bin/pip install zc.buildout==2.13.6
bin/buildout
