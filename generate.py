# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Generate the necessary data files and directory structures from the Debian
project's data."""

import os.path
import shutil

STANDARDS = ['639', '3166', '4217', '15924']


data_dir = 'data'
base_dir = os.path.join('src', 'pycountry')

assert os.path.exists(base_dir), 'pycountry src directory not found'
assert os.path.exists(data_dir), 'pkg-isocodes data directory not found'

database_dir = os.path.join(base_dir, 'databases')
locales_dir = os.path.join(base_dir, 'locales')


# Put the database files in place
if not os.path.exists(database_dir):
    os.mkdir(database_dir)

for standard in STANDARDS:
    src = os.path.join('data', 'iso_%s' % standard, 'iso_%s.xml' % standard)
    dst = os.path.join(database_dir, 'iso%s.xml' % standard)
    shutil.copyfile(src, dst)
