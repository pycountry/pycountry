"""pycountry"""

import os.path
import unicodedata
from functools import cached_property
from importlib import metadata as _importlib_metadata
from typing import Dict, List, Optional, Set, Type, cast

import pycountry.db
from pycountry.db import Country as Country
from pycountry.db import Subdivision as Subdivision

# We prioritise importing the backported `importlib_resources`
# because the function we use (`importlib.resources.files`) is only
# available from Python 3.9, but the module itself exists since 3.7.
# We install `importlib_resources` on Python < 3.9.
# TODO: Remove usage of importlib_resources once support for Python 3.8 is dropped
try:
    import importlib_resources  # type: ignore
except ModuleNotFoundError:
    from importlib import resources as importlib_resources  # type: ignore


def resource_filename(package_or_requirement: str, resource_name: str) -> str:
    return str(
        importlib_resources.files(package_or_requirement) / resource_name
    )


def get_version(distribution_name: str) -> Optional[str]:
    try:
        return _importlib_metadata.version(distribution_name)
    except _importlib_metadata.PackageNotFoundError:
        return "n/a"


# Variable annotations
LOCALES_DIR: str = resource_filename("pycountry", "locales")
DATABASE_DIR: str = resource_filename("pycountry", "databases")
__version__: Optional[str] = get_version("pycountry")


def remove_accents(input_str: str) -> str:
    output_str = input_str
    if not input_str.isascii():
        # Borrowed from https://stackoverflow.com/a/517974/1509718
        nfkd_form = unicodedata.normalize("NFKD", input_str)
        output_str = "".join(
            [c for c in nfkd_form if not unicodedata.combining(c)]
        )
    return output_str


class ExistingCountries(pycountry.db.Database[pycountry.db.Country]):
    """Provides access to an ISO 3166 database (Countries)."""

    factory = pycountry.db.Country
    root_key = "3166-1"

    def search_fuzzy(self, query: str) -> List[pycountry.db.Country]:
        query = remove_accents(query.strip().lower())

        # A country-code to points mapping for later sorting countries
        # based on the query's matching incidence.
        results: dict[str, int] = {}

        def add_result(country: "pycountry.db.Country", points: int) -> None:
            results.setdefault(country.alpha_2, 0)
            results[country.alpha_2] += points

        # Prio 1: exact matches on country names
        try:
            add_result(self.lookup(query), 50)
        except LookupError:
            pass

        # Prio 2: exact matches on subdivision names
        match_subdivions = subdivisions.match(query=query)
        for subdivision in match_subdivions:
            add_result(subdivision.country, 49)

        # Prio 3: partial matches on country names
        for country in self:
            # Higher priority for a match on the common name
            for v in [
                country._fields.get("name"),
                country._fields.get("official_name"),
                country._fields.get("comment"),
            ]:
                if v is not None:
                    v = remove_accents(v.lower())
                    if query in v:
                        # This prefers countries with a match early in their name
                        # and also balances against countries with a number of
                        # partial matches and their name containing 'new' in the
                        # middle
                        add_result(country, max([5, 30 - (2 * v.find(query))]))
                        break

        # Prio 4: partial matches on subdivision names
        partial_match_subdivisions = subdivisions.partial_match(query=query)
        for subdivision in partial_match_subdivisions:
            v = subdivision._fields.get("name")
            assert v
            v = remove_accents(v.lower())
            if query in v:
                add_result(subdivision.country, max([1, 5 - v.find(query)]))

        if not results:
            raise LookupError(query)

        sorted_results = [
            cast(pycountry.db.Country, self.get(alpha_2=x[0]))
            # sort by points first, by alpha2 code second, and to ensure stable
            # results the negative value allows us to sort reversely on the
            # points but ascending on the country code.
            for x in sorted(results.items(), key=lambda x: (-x[1], x[0]))
        ]
        return sorted_results


class HistoricCountries(ExistingCountries):
    """Provides access to an ISO 3166-3 database
    (Countries that have been removed from the standard)."""

    factory = pycountry.db.Country
    root_key = "3166-3"


class Script(pycountry.db.Data):
    pass


class Scripts(pycountry.db.Database[Script]):
    """Provides access to an ISO 15924 database (Scripts)."""

    factory = Script
    root_key = "15924"


class Currency(pycountry.db.Data):
    pass


class Currencies(pycountry.db.Database[Currency]):
    """Provides access to an ISO 4217 database (Currencies)."""

    factory = Currency
    root_key = "4217"


class Language(pycountry.db.Data):
    pass


class Languages(pycountry.db.Database[Language]):
    """Provides access to an ISO 639-1/2T/3 database (Languages)."""

    no_index = ["status", "scope", "type", "inverted_name", "common_name"]

    factory = Language
    root_key = "639-3"


class LanguageFamily(pycountry.db.Data):
    pass


class LanguageFamilies(pycountry.db.Database[LanguageFamily]):
    """Provides access to an ISO 639-5 database
    (Language Families and Groups)."""

    factory = LanguageFamily
    root_key = "639-5"


class SubdivisionHierarchy(pycountry.db.Data):
    @property
    def country(self) -> pycountry.db.Country:
        return cast(
            pycountry.db.Country, countries.get(alpha_2=self.country_code)
        )

    @cached_property
    def country_code(self) -> str:
        return self.code.split("-")[0]

    @property
    def parent(self) -> Optional["SubdivisionHierarchy"]:
        if not self.parent_code:
            return None
        return subdivisions.get(code=self.parent_code)

    @cached_property
    def parent_code(self) -> Optional[str]:
        parent = self._fields.get("parent")
        if parent is not None:
            # check if the country_code is already present
            parts = parent.split("-")
            if parts[0] != self.country_code:
                parent = f"{self.country_code}-{parent}"

        return parent


class Subdivisions(pycountry.db.Database[SubdivisionHierarchy]):
    # Note: subdivisions can be hierarchical to other subdivisions. The
    # parent_code attribute is related to other subdivisions, *not*
    # the country!

    factory = SubdivisionHierarchy
    no_index = ["name", "parent_code", "parent", "type"]
    root_key = "3166-2"

    def _load(self) -> None:
        super()._load()

        # Add index for the country code.
        self.indices["country_code"] = {}
        for subdivision in self:
            divs = cast(
                Set[SubdivisionHierarchy],
                self.indices["country_code"].setdefault(
                    subdivision.country_code.lower(), set()  # type: ignore[arg-type]
                ),
            )
            divs.add(subdivision)

    def get(
        self, *, default: Optional[SubdivisionHierarchy] = None, **kw: str
    ) -> Optional[SubdivisionHierarchy]:
        result = super().get(default=default, **kw)
        if result is default and "country_code" in kw:
            # This handles the case where we know about a country but there
            # are no subdivisions: we return an empty list in this case
            # (sticking to the expected type here) instead of None.
            if countries.get(alpha_2=kw["country_code"]) is not None:
                return []  # type: ignore[return-value]
        return result

    def match(self, query: str) -> List[SubdivisionHierarchy]:
        query = remove_accents(query.strip().lower())
        matching_candidates = []
        for candidate in self:
            for v in candidate._fields.values():
                if v is not None:
                    v = remove_accents(v.lower())
                    # Some names include alternative versions which we want to
                    # match exactly.
                    for w in v.split(";"):
                        if w == query:
                            matching_candidates.append(candidate)
                            break

        return matching_candidates

    def partial_match(self, query: str) -> List[SubdivisionHierarchy]:
        query = remove_accents(query.strip().lower())
        matching_candidates = []
        for candidate in self:
            v = candidate._fields.get("name")
            assert v
            v = remove_accents(v.lower())
            if query in v:
                matching_candidates.append(candidate)

        return matching_candidates

    def search_fuzzy(self, query: str) -> List[SubdivisionHierarchy]:
        query = remove_accents(query.strip().lower())

        # A Subdivision's code to points mapping for later sorting subdivisions
        # based on the query's matching incidence.
        results: dict[str, int] = {}

        def add_result(
            subdivision: "pycountry.SubdivisionHierarchy", points: int
        ) -> None:
            results.setdefault(subdivision.code, 0)
            results[subdivision.code] += points

        # Prio 1: exact matches on subdivision names
        match_subdivisions = self.match(query)
        for candidate in match_subdivisions:
            add_result(candidate, 50)

        # Prio 2: partial matches on subdivision names
        partial_match_subdivisions = self.partial_match(query)
        for candidate in partial_match_subdivisions:
            v = candidate._fields.get("name")
            assert v
            v = remove_accents(v.lower())
            if query in v:
                add_result(candidate, max([1, 5 - v.find(query)]))

        if not results:
            raise LookupError(query)

        sorted_results = [
            cast(SubdivisionHierarchy, self.get(code=x[0]))
            # sort by points first, by alpha2 code second, and to ensure stable
            # results the negative value allows us to sort reversely on the
            # points but ascending on the country code.
            for x in sorted(results.items(), key=lambda x: (-x[1], x[0]))
        ]
        return sorted_results


# Initialize instances with type hints
countries = ExistingCountries(os.path.join(DATABASE_DIR, "iso3166-1.json"))
subdivisions = Subdivisions(os.path.join(DATABASE_DIR, "iso3166-2.json"))
historic_countries = HistoricCountries(
    os.path.join(DATABASE_DIR, "iso3166-3.json")
)

currencies = Currencies(os.path.join(DATABASE_DIR, "iso4217.json"))

languages = Languages(os.path.join(DATABASE_DIR, "iso639-3.json"))
language_families = LanguageFamilies(
    os.path.join(DATABASE_DIR, "iso639-5.json")
)

scripts = Scripts(os.path.join(DATABASE_DIR, "iso15924.json"))
