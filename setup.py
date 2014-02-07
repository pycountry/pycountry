# vim:fileencoding=utf-8
# Copyright (c) gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
from setuptools import setup, find_packages


setup(
    name='pycountry',
    version='1.4',
    author='Christian Theune',
    author_email='ct@gocept.com',
    description='ISO country, subdivision, language, currency and script '
                'definitions and their translations',
    long_description=(
        open('README').read() + '\n' +
        open('HISTORY.txt').read()),
    license='LGPL 2.1',
    keywords='country subdivision language currency iso 3166 639 4217 '
             '15924 3166-2',
    zip_safe=False,
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'})
