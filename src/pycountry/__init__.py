# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""pycountry"""

import os.path

import pycountry.db


class Countries(pycountry.db.Database):
    """Provides access to an ISO 3166 database."""

    field_map = dict(alpha_2_code='alpha2',
                     alpha_3_code='alpha3',
                     numeric_code='numeric',
                     name='name',
                     official_name='official_name',
                     common_name='common_name')
    data_class_name = 'Country'
    xml_tag = 'iso_3166_entry'


database_dir = os.path.join(os.path.dirname(__file__), 'databases')

countries = Countries(os.path.join(database_dir, 'iso3166.xml'))
