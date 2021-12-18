# vim:fileencoding=utf-8
"""pycountry"""

import os.path
import re
import unicodedata
from functools import cache

import pycountry.db


try:
    import pkg_resources
    resource_filename = pkg_resources.resource_filename
    __version__ = pkg_resources.get_distribution("pycountry").version
except ImportError:
    __version__ = 'n/a'

    def resource_filename(package_or_requirement, resource_name):
        return os.path.join(os.path.dirname(__file__), resource_name)




LOCALES_DIR = resource_filename('pycountry', 'locales')
DATABASE_DIR = resource_filename('pycountry', 'databases')
LEXRES_DIR = resource_filename('pycountry', 'lexical_resources')

def remove_accents(input_str):
    # Borrowed from https://stackoverflow.com/a/517974/1509718
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

re_nonalpha = re.compile("\W+")
re_stopwords = re.compile("(and|or|the|of)", re.IGNORECASE)

def normalize(s):
    s = remove_accents(s.strip().lower())
    s = re_stopwords.sub(" ", s)
    s = re_nonalpha.sub(" ", s) # this also combines multiple spaces
    return s


class Country(): # this is just to make life easier for IDEs etc.
    alpha_2:str = property()
    alpha_3:str = property()
    name:str = property()
    official_name:str = property()
    numeric:str = property()


class ExistingCountries(pycountry.db.Database):
    """Provides access to an ISO 3166 database (Countries)."""

    data_class_name = 'Country'
    root_key = '3166-1'


    @cache # this is important, otherwise it'll regenerate the database every time it's queried!
    def wikipedia_redirects(self, aggressively_normalize=False):
        wik_redirs = dict()
        with open(os.path.join(LEXRES_DIR, "existingcountries_wikipedia_redirects.tab"), "rt") as f:
            for line in f:
                [twoletter, displaytitle, alias] = line.strip().split("\t")
                if aggressively_normalize:
                    term = normalize(alias)
                else:
                    term = remove_accents(alias.strip().lower())

                if term in wik_redirs and wik_redirs[term] != twoletter:
                    print("clash! {} and {} both can be got to from {}")
                else:
                    wik_redirs[term] = twoletter
        return(wik_redirs)


    def search_fuzzy(self, query):
        query = remove_accents(query.strip().lower())

        # A country-code to points mapping for later sorting countries
        # based on the query's matching incidence.
        results = {}

        def add_result(country, points, is_already_alpha_2 = False):
            if is_already_alpha_2:
                a2 = country
            else:
                a2 = country.alpha_2
            results.setdefault(a2, 0)
            results[a2] += points

        # Prio 1: exact matches on country names
        try:
            add_result(self.lookup(query), 50)
        except LookupError:
            pass

        # Prio 1.5: exact matches on wikipedia redirect names:
        if self.__class__ == ExistingCountries: # assuming data for historic countries not generated.
            if query in self.wikipedia_redirects():
                add_result(self.wikipedia_redirects()[query], 49, is_already_alpha_2=True)
            elif normalize(query) in self.wikipedia_redirects(aggressively_normalize = True):
                add_result(self.wikipedia_redirects(aggressively_normalize = True)[normalize(query)], 45, is_already_alpha_2=True)


        # Prio 2: exact matches on subdivision names
        for candidate in subdivisions:
            for v in candidate._fields.values():
                if v is None:
                    continue
                v = remove_accents(v.lower())
                # Some names include alternative versions which we want to
                # match exactly.
                for v in v.split(';'):
                    if v == query:
                        add_result(candidate.country, 40)
                        break

        # Prio 3: partial matches on country names
        for candidate in self:
            # Higher priority for a match on the common name
            for v in [candidate._fields.get('name'),
                      candidate._fields.get('official_name'),
                      candidate._fields.get('comment')]:
                if v is None:
                    continue
                v = remove_accents(v.lower())
                if query in v:
                    # This prefers countries with a match early in their name
                    # and also balances against countries with a number of
                    # partial matches and their name containing 'new' in the
                    # middle
                    add_result(candidate, max([5, 30-(2*v.find(query))]))
                    break

        # Prio 4: partial matches on subdivision names
        for candidate in subdivisions:
            v = candidate._fields.get('name')
            if v is None:
                continue
            v = remove_accents(v.lower())
            if query in v:
                add_result(candidate.country, max([1, 5-v.find(query)]))

        if not results:
            raise LookupError(query)

        results = [
            self.get(alpha_2=x[0])
            # sort by points first, by alpha2 code second, and to ensure stable
            # results the negative value allows us to sort reversely on the
            # points but ascending on the country code.
            for x in sorted(results.items(),
                            key=lambda x: (-x[1], x[0]))]
        return results


class HistoricCountries(ExistingCountries):
    """Provides access to an ISO 3166-3 database
    (Countries that have been removed from the standard)."""

    data_class_name = 'Country'
    root_key = '3166-3'


class Scripts(pycountry.db.Database):
    """Provides access to an ISO 15924 database (Scripts)."""

    data_class_name = 'Script'
    root_key = '15924'


class Currencies(pycountry.db.Database):
    """Provides access to an ISO 4217 database (Currencies)."""

    data_class_name = 'Currency'
    root_key = '4217'


class Languages(pycountry.db.Database):
    """Provides access to an ISO 639-1/2T/3 database (Languages)."""

    no_index = ['status', 'scope', 'type', 'inverted_name', 'common_name']
    data_class_name = 'Language'
    root_key = '639-3'


class LanguageFamilies(pycountry.db.Database):
    """Provides access to an ISO 639-5 database
       (Language Families and Groups)."""

    data_class_name = 'LanguageFamily'
    root_key = '639-5'


class Subdivision(pycountry.db.Data):

    def __init__(self, **kw):
        if 'parent' in kw:
            kw['parent_code'] = kw['parent']
        else:
            kw['parent_code'] = None
        super(Subdivision, self).__init__(**kw)
        self.country_code = self.code.split('-')[0]
        if self.parent_code is not None:
            self.parent_code = '%s-%s' % (self.country_code, self.parent_code)

    @property
    def country(self):
        return countries.get(alpha_2=self.country_code)

    @property
    def parent(self):
        if not self.parent_code:
            return None
        return subdivisions.get(code=self.parent_code)


class Subdivisions(pycountry.db.Database):

    # Note: subdivisions can be hierarchical to other subdivisions. The
    # parent_code attribute is related to other subdivisons, *not*
    # the country!

    data_class_base = Subdivision
    data_class_name = 'Subdivision'
    no_index = ['name', 'parent_code', 'parent', 'type']
    root_key = '3166-2'

    def _load(self, *args, **kw):
        super(Subdivisions, self)._load(*args, **kw)

        # Add index for the country code.
        self.indices['country_code'] = {}
        for subdivision in self:
            divs = self.indices['country_code'].setdefault(
                subdivision.country_code.lower(), set())
            divs.add(subdivision)

    def get(self, **kw):
        default = kw.setdefault('default', None)
        subdivisions = super(Subdivisions, self).get(**kw)
        if subdivisions is default and 'country_code' in kw:
            # This handles the case where we know about a country but there
            # are no subdivisions: we return an empty list in this case
            # (sticking to the expected type here) instead of None.
            if countries.get(alpha_2=kw['country_code']) is not None:
                return []
        return subdivisions


countries:list[Country] = ExistingCountries(os.path.join(DATABASE_DIR, 'iso3166-1.json'))
subdivisions = Subdivisions(os.path.join(DATABASE_DIR, 'iso3166-2.json'))
historic_countries = HistoricCountries(
    os.path.join(DATABASE_DIR, 'iso3166-3.json'))

currencies = Currencies(os.path.join(DATABASE_DIR, 'iso4217.json'))

languages = Languages(os.path.join(DATABASE_DIR, 'iso639-3.json'))
language_families = LanguageFamilies(
    os.path.join(DATABASE_DIR, 'iso639-5.json'))

scripts = Scripts(os.path.join(DATABASE_DIR, 'iso15924.json'))
