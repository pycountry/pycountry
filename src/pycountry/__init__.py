# vim:fileencoding=utf-8
"""pycountry"""

import os.path

import pycountry.db

try:
    from pkg_resources import resource_filename
except ImportError:
    def resource_filename(package_or_requirement, resource_name):
        return os.path.join(os.path.dirname(__file__), resource_name)


LOCALES_DIR = resource_filename('pycountry', 'locales')
DATABASE_DIR = resource_filename('pycountry', 'databases')


class CountriesBase(pycountry.db.Database):
    """Provides access to an ISO 3166 database (Countries)."""

    field_map = dict(alpha_2_code='alpha2',
                     alpha_3_code='alpha3',
                     numeric_code='numeric',
                     official_name='official_name',
                     common_name='common_name')
    data_class_name = 'Country'


class ExistingCountries(CountriesBase):
    """Provides access to an ISO 3166 database (Countries)."""

    field_map = dict(name='name',
                     **CountriesBase.field_map)
    xml_tags = 'iso_3166_entry'


def choose_alpha2(record):
    if hasattr(record, 'alpha2'):
        return record.alpha2
    return record.alpha4[:2]


class HistoricCountries(CountriesBase):
    """Provides access to an ISO 3166-3 database
    (Countries that have been removed from the standard)."""

    field_map = dict(alpha_4_code='alpha4',
                     date_withdrawn='date_withdrawn',
                     name='name',
                     names='name',
                     comment='comment',
                     **CountriesBase.field_map)

    # These fields are computed in a case-by-base basis
    # `alpha2` is not set in ISO-3166-3, so, we extract it from `alpha4`

    generated_fields = dict(
        alpha2=choose_alpha2,
        deleted=lambda x: hasattr(x, 'date_withdrawn'))
    xml_tags = ['iso_3166_entry', 'iso_3166_3_entry']


class Scripts(pycountry.db.Database):
    """Providess access to an ISO 15924 database (Scripts)."""

    field_map = dict(alpha_4_code='alpha4',
                     numeric_code='numeric',
                     name='name')
    data_class_name = 'Script'
    xml_tags = 'iso_15924_entry'


class Currencies(pycountry.db.Database):
    """Providess access to an ISO 4217 database (Currencies)."""

    field_map = dict(letter_code='letter',
                     numeric_code='numeric',
                     currency_name='name')
    data_class_name = 'Currency'
    xml_tags = 'iso_4217_entry'


class Languages(pycountry.db.Database):
    """Providess access to an ISO 639-1/2T/3 database (Languages)."""

    field_map = dict(id='iso639_3_code',
                     part1_code='iso639_1_code',
                     part2_code='iso639_2T_code',
                     status='status',
                     scope='scope',
                     type='type',
                     inverted_name='inverted_name',
                     reference_name='reference_name',
                     name='name',
                     common_name='common_name'
                     )
    no_index = ['terminology', 'status', 'scope', 'type', 'inverted_name',
                'reference_name', 'common_name']
    data_class_name = 'Language'
    xml_tags = 'iso_639_3_entry'


class Subdivision(pycountry.db.Data):

    parent_code = None

    def __init__(self, element, **kw):
        super(Subdivision, self).__init__(element, **kw)
        self.type = element.parentNode.attributes.get('type').value
        self.country_code = self.code.split('-')[0]
        if self.parent_code is not None:
            self.parent_code = '%s-%s' % (self.country_code, self.parent_code)

    @property
    def country(self):
        return countries.get(alpha2=self.country_code)

    @property
    def parent(self):
        if not self.parent_code:
            return None
        return subdivisions.get(code=self.parent_code)


class Subdivisions(pycountry.db.Database):

    # Note: subdivisions can be hierarchical to other subdivisions. The
    # parent_code attribute is related to other subdivisons, *not*
    # the country!

    xml_tags = 'iso_3166_2_entry'
    data_class_base = Subdivision
    data_class_name = 'Subdivision'
    field_map = dict(code='code',
                     name='name',
                     parent='parent_code')
    no_index = ['name', 'parent_code']

    def _load(self, *args, **kw):
        super(Subdivisions, self)._load(*args, **kw)

        # Add index for the country code.
        self.indices['country_code'] = {}
        for subdivision in self:
            divs = self.indices['country_code'].setdefault(
                subdivision.country_code, set())
            divs.add(subdivision)


countries = ExistingCountries(os.path.join(DATABASE_DIR, 'iso3166.xml'))
historic_countries = HistoricCountries(
    os.path.join(DATABASE_DIR, 'iso3166.xml'))
scripts = Scripts(os.path.join(DATABASE_DIR, 'iso15924.xml'))
currencies = Currencies(os.path.join(DATABASE_DIR, 'iso4217.xml'))
languages = Languages(os.path.join(DATABASE_DIR, 'iso639_3.xml'))
subdivisions = Subdivisions(os.path.join(DATABASE_DIR, 'iso3166_2.xml'))
