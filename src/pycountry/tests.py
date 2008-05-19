# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Test harness for pycountry."""

import doctest
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('README.txt',
                                       optionflags=doctest.ELLIPSIS))
    return suite
