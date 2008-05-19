# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Generate the necessary data files and directory structures from the Debian
project's data."""

import glob
import os.path
import shutil
import subprocess

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


# Put the PO files in place and compile them
for standard in STANDARDS:
    locale_dir = os.path.join(data_dir, 'iso_%s' % standard)
    for src in glob.glob(os.path.join(locale_dir, '*.po')):
        dir, locale = os.path.split(src)
        locale = locale.replace('.po', '')

        dst_dir = os.path.join(locales_dir, locale, 'LC_MESSAGES')
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        dst = os.path.join(dst_dir, 'iso%s.po' % standard)
        dst_mo = dst.replace('.po', '.mo')

        shutil.copyfile(src, dst)

        subprocess.check_call(['msgfmt', dst, '-o', dst_mo])


# Generate the MO files.
