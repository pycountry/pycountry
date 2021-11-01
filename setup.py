# vim:fileencoding=utf-8
# Copyright -2014 (c) gocept gmbh & co. kg
# Copyright 2015- (c) Flying Circus Internet Operations GmbH
# See also LICENSE.txt

from io import open

from setuptools import setup, find_packages


setup(
    name='iroin_pycountry',
    version='20.7.6',
    author='Christian Theune',
    author_email='oss@iroin.io',
    description='ISO country, subdivision, language, currency and script '
                'definitions and their translations',
    long_description=(
        open('README.rst', encoding='utf-8').read() + '\n' +
        open('HISTORY.txt', encoding='utf-8').read()),
    url='https://github.com/iroin/pycountry',
    license='LGPL 2.1',
    keywords='country subdivision language currency iso 3166 639 4217 '
             '15924 3166-2',
    classifiers=[
        # See: https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
    ],
    python_requires='>=3.5, <4',
    install_requires=['setuptools'],  # pkg_resources
    zip_safe=False,
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'})
