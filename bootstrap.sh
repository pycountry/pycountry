#!/bin/sh
set -ex
rm -rf bin develop-eggs eggs include lib parts
virtualenv --python=python3 .
bin/pip install zc.buildout
bin/pip install tox
bin/buildout
