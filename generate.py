# Copyright (c) 2008 gocept gmbh & co. kg
# Copyright (c) 2014+ Christian Theune, christian@theune.cc
# See also LICENSE.txt
# $Id$
"""Generate the necessary data files and directory structures from the Debian
project's data."""

import glob
import os.path
import shutil
import subprocess

REVISION = "v4.15.0"

data_dir = "parts/data"
base_dir = os.path.join("src", "pycountry")

if not os.path.exists(data_dir):
    subprocess.check_call(
        [
            "git",
            "clone",
            "https://salsa.debian.org/iso-codes-team/iso-codes.git",
            data_dir,
        ]
    )

subprocess.check_call(["git", "-C", data_dir, "fetch"])
subprocess.check_call(["git", "-C", data_dir, "checkout", REVISION])


assert os.path.exists(base_dir), "pycountry src directory not found"
assert os.path.exists(data_dir), "pkg-isocodes data directory not found"

database_dir = os.path.join(base_dir, "databases")
locales_dir = os.path.join(base_dir, "locales")


STANDARDS = ["639-3", "639-5", "3166-1", "3166-2", "3166-3", "4217", "15924"]

# Put the database files in place
if not os.path.exists(database_dir):
    os.mkdir(database_dir)

for standard in STANDARDS:
    src = os.path.join(data_dir, "data", "iso_%s.json" % standard)
    print(src)
    dst = os.path.join(database_dir, "iso%s.json" % standard)
    shutil.copyfile(src, dst)


# Put the PO files in place and compile them
for standard in STANDARDS:
    for src in glob.glob(os.path.join(data_dir, f"iso_{standard}", "*.po")):
        print(src)
        dir, locale = os.path.split(src)
        locale = locale.replace(".po", "")

        dst_dir = os.path.join(locales_dir, locale, "LC_MESSAGES")
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        dst = os.path.join(dst_dir, "iso%s.po" % standard)
        dst_mo = dst.replace(".po", ".mo")

        shutil.copyfile(src, dst)
        print(src + " -> " + dst)
        subprocess.check_call(["msgfmt", dst, "-o", dst_mo])
        os.unlink(dst)


# Generate the MO files.
