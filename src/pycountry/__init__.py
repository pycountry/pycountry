# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""pycountry"""

import os.path

import pycountry.db


class Countries(pycountry.db.Database):
    """Provides access to an ISO 3166 database (Countries)."""

    field_map = dict(alpha_2_code='alpha2',
                     alpha_3_code='alpha3',
                     numeric_code='numeric',
                     name='name',
                     official_name='official_name',
                     common_name='common_name')
    data_class_name = 'Country'
    xml_tag = 'iso_3166_entry'


class Scripts(pycountry.db.Database):
    """Providess access to an ISO 15924 database (Scripts)."""

    field_map = dict(alpha_4_code='alpha4',
                     numeric_code='numeric',
                     name='name')
    data_class_name = 'Script'
    xml_tag = 'iso_15924_entry'


class Currencies(pycountry.db.Database):
    """Providess access to an ISO 4217 database (Currencies)."""

    field_map = dict(letter_code='letter',
                     numeric_code='numeric',
                     currency_name='name')
    data_class_name = 'Currency'
    xml_tag = 'iso_4217_entry'

database_dir = os.path.join(os.path.dirname(__file__), 'databases')

countries = Countries(os.path.join(database_dir, 'iso3166.xml'))
scripts = Scripts(os.path.join(database_dir, 'iso15924.xml'))
currencies  = Currencies(os.path.join(database_dir, 'iso4217.xml'))
