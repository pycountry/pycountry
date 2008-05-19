# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""pycountry"""

import os.path
import lxml.etree

database_dir = os.path.join(os.path.dirname(__file__), 'databases')


class Data(object):
    pass


class Countries(object):

    field_map = dict(alpha_2_code='alpha2',
                     alpha_3_code='alpha3',
                     numeric_code='numeric',
                     name='name',
                     official_name='official_name',
                     common_name='common_name')

    def __init__(self, filename):
        self.objects = []
        self.indices = {}

        self.data_class = type('Country', (Data,), {})

        f = open(filename, 'rb')
        etree = lxml.etree.parse(f)

        for entry in etree.xpath('//iso_3166_entry'):
            entry_obj = self.data_class()
            for key in entry.keys():
                setattr(entry_obj, self.field_map[key], entry.get(key))
            self.objects.append(entry_obj)

        # Create indices
        for key in self.field_map.values():
            self.indices[key] = {}

        # Update indices
        for obj in self.objects:
            for key in self.field_map.values():
                value = getattr(obj, key, None)
                if value is None:
                    continue
                assert value not in self.indices[key], (
                    'Entry %r already taken in index %r' % (value, key))
                self.indices[key][value] = obj

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    def get(self, **kw):
        assert len(kw) == 1, 'Only one criteria may be given.'
        field, value = kw.items()[0]
        return self.indices[field][value]


countries = Countries(os.path.join(database_dir, 'iso3166.xml'))
