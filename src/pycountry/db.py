# vim:fileencoding=utf-8

from contextlib import closing
from xml.dom import minidom
import logging

logger = logging.getLogger('pycountry.db')


class Data(object):

    def __init__(self, element, **fields):
        self._fields = fields

    def __getattr__(self, key):
        if key not in self._fields:
            raise AttributeError
        return self._fields[key]

    def __setattr__(self, key, value):
        if key != '_fields':
            self._fields[key] = value
        super(Data, self).__setattr__(key, value)

    def __repr__(self):
        cls_name = self.__class__.__name__
        fields = ', '.join('%s=%r' % i for i in sorted(self._fields.items()))
        return '%s(%s)' % (cls_name, fields)

    def __dir__(self):
        return dir(self.__class__) + list(self._fields)


def lazy_load(f):
    def load_if_needed(self, *args, **kw):
        if not self._is_loaded:
            self._load()
        return f(self, *args, **kw)
    return load_if_needed


class Database(object):

    # Override those names in sub-classes for specific ISO database.
    field_map = dict()
    generated_fields = dict()
    data_class_base = Data
    data_class_name = None
    xml_tags = None
    no_index = []

    def __init__(self, filename):
        self.filename = filename
        self._is_loaded = False

    def _load(self):
        self.objects = []
        self.indices = {}

        if isinstance(self.xml_tags, str):
            tags = [self.xml_tags]
        else:
            tags = self.xml_tags

        self.data_class = type(
            self.data_class_name, (self.data_class_base,), {})

        with closing(open(self.filename, 'rb')) as f:
            tree = minidom.parse(f)

        for tag in tags:
            for entry in tree.getElementsByTagName(tag):
                mapped_data = {}
                for key in entry.attributes.keys():
                    mapped_data[self.field_map[key]] = (
                        entry.attributes.get(key).value)
                entry_obj = self.data_class(entry, **mapped_data)
                self.objects.append(entry_obj)

        tree.unlink()

        # Construct list of indices: primary single-column indices
        indices = []

        for key in self.field_map.values():
            if key in self.no_index:
                continue
            else:
                # Slightly horrible hack: to evaluate `key` at definition time
                # of the lambda I pass it as a keyword argument.
                def getter(x, key=key):
                    return getattr(x, key, None)
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
                    logger.debug(
                        '%s %r already taken in index %r and will be '
                        'ignored. This is an error in the XML databases.' %
                        (self.data_class_name, value, name))
                self.indices[name][value] = obj

        self._add_generated_fields()
        self._is_loaded = True

    def _add_generated_fields(self):
        for key in self.generated_fields:
            self.indices[key] = {}

        for obj in self.objects:
            for name, rule in self.generated_fields.items():
                value = rule(obj)

                setattr(obj, name, value)

                if value in self.indices[name]:
                    logger.debug(
                        '%s %r already taken in index %r and will be '
                        'ignored.' % (self.data_class_name, value, name))
                self.indices[name][value] = obj

    # Public API

    @lazy_load
    def __iter__(self):
        return iter(self.objects)

    @lazy_load
    def __len__(self):
        return len(self.objects)

    @lazy_load
    def get(self, **kw):
        if len(kw) != 1:
            raise TypeError('Only one criteria may be given')
        field, value = kw.popitem()
        return self.indices[field][value]

    @lazy_load
    def lookup(self, value):
        keys = sorted(set(self.field_map.values()).union(
                      set(self.generated_fields)).difference(
                      set(self.no_index)))
        # try relatively quick exact matches first
        for key in keys:
            try:
                return self.indices[key][value]
            except LookupError:
                pass
        # then try slower case-insensitive lookups
        for key in keys:
            d = self.indices[key]
            for k, v in d.items():
                try:
                    if k.lower() == value.lower():
                        return v
                except AttributeError:
                    pass
        raise LookupError('Could not find a record for %r' % value)
