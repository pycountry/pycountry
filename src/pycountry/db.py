# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Generic database code."""

import logging
import lxml.etree

logger = logging.getLogger('pycountry.db')


class Data(object):

    def __init__(self, element, **kw):
        self._element = element
        for key, value in kw.items():
            setattr(self, key, value)


class Database(object):

    # Override those names in sub-classes for specific ISO database.
    field_map = dict()
    data_class_base = Data
    data_class_name = None
    xml_tag = None
    no_index = []

    def __init__(self, filename):
        self.objects = []
        self.indices = {}

        self.data_class = type(self.data_class_name, (self.data_class_base,),
                               {})

        f = open(filename, 'rb')
        etree = lxml.etree.parse(f)

        for entry in etree.xpath('//%s' % self.xml_tag):
            mapped_data = {}
            for key in entry.keys():
                mapped_data[self.field_map[key]] = entry.get(key)
            entry_obj = self.data_class(entry, **mapped_data)
            self.objects.append(entry_obj)

        # Construct list of indices: primary single-column indices
        indices = []
        for key in self.field_map.values():
            if key in self.no_index:
                continue
            # Slightly horrible hack: to evaluate `key` at definition time of
            # the lambda I pass it as a keyword argument.
            getter = lambda x, key=key: getattr(x, key, None)
            indices.append((key, getter))

        # Create indices
        for name, _ in indices:
            self.indices[name] = {}

        # Update indices
        for obj in self.objects:
            for name, rule in indices:
                value = rule(obj)
                if value is None:
                    continue
                if value in self.indices[name]:
                    logger.error(
                        '%s %r already taken in index %r and will be '
                        'ignored. This is an error in the XML databases.' %
                        (self.data_class_name, value, name))
                self.indices[name][value] = obj

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    def get(self, **kw):
        assert len(kw) == 1, 'Only one criteria may be given.'
        field, value = kw.items()[0]
        return self.indices[field][value]
