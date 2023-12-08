"""pycountry"""

import os.path
import unicodedata
from importlib import metadata as importlib_metadata
from typing import Dict, List, Optional, Type

import pycountry.db

# We prioritise importing the backported `importlib_resources`
# because the function we use (`importlib.resources.files`) is only
# available from Python 3.9, but the module itself exists since 3.7.
# We install `importlib_resources` on Python < 3.9.
# TODO: Remove usage of importlib_resources once support for Python 3.8 is dropped
try:
    import importlib_resources
except ModuleNotFoundError:
    from importlib import resources as importlib_resources


def resource_filename(package_or_requirement: str, resource_name: str) -> str:
    return str(
        importlib_resources.files(package_or_requirement) / resource_name
    )


def get_version(distribution_name: str) -> Optional[str]:
    try:
        return importlib_metadata.version(distribution_name)
    except importlib_metadata.PackageNotFoundError:
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


class ExistingCountries(pycountry.db.Database):
    """Provides access to an ISO 3166 database (Countries)."""

    def __init__(self, filename: str) -> None:
        super().__init__(filename, data_class_name="Country")
        self.root_key = "3166-1"

    def search_fuzzy(self, query: str) -> List[Type["ExistingCountries"]]:
        query = remove_accents(query.strip().lower())

        # A country-code to points mapping for later sorting countries
        # based on the query's matching incidence.
        results: dict[str, int] = {}

        def add_result(country: Type["ExistingCountries"], points: int) -> None:
            results.setdefault(country.alpha_2, 0)
            results[country.alpha_2] += points

        # Prio 1: exact matches on country names
        try:
            add_result(self.lookup(query), 50)
        except LookupError:
            pass

        # Prio 2: exact matches on subdivision names
        for candidate in subdivisions:
            for v in candidate._fields.values():
                if v is None:
                    continue
                v = remove_accents(v.lower())
                # Some names include alternative versions which we want to
                # match exactly.
                for v in v.split(";"):
                    if v == query:
                        add_result(candidate.country, 49)
                        break

        # Prio 3: partial matches on country names
        for candidate in self:
            # Higher priority for a match on the common name
            for v in [
                candidate._fields.get("name"),
                candidate._fields.get("official_name"),
                candidate._fields.get("comment"),
            ]:
                if v is None:
                    continue
                v = remove_accents(v.lower())
                if query in v:
                    # This prefers countries with a match early in their name
                    # and also balances against countries with a number of
                    # partial matches and their name containing 'new' in the
                    # middle
                    add_result(candidate, max([5, 30 - (2 * v.find(query))]))
                    break

        # Prio 4: partial matches on subdivision names
        for candidate in subdivisions:
            v = candidate._fields.get("name")
            if v is None:
                continue
            v = remove_accents(v.lower())
            if query in v:
                add_result(candidate.country, max([1, 5 - v.find(query)]))

        if not results:
            raise LookupError(query)

        results = [
            self.get(alpha_2=x[0])
            # sort by points first, by alpha2 code second, and to ensure stable
            # results the negative value allows us to sort reversely on the
            # points but ascending on the country code.
            for x in sorted(results.items(), key=lambda x: (-x[1], x[0]))
        ]
        return results


class HistoricCountries(ExistingCountries):
    """Provides access to an ISO 3166-3 database
    (Countries that have been removed from the standard)."""

    def __init__(self, filename: str) -> None:
        super().__init__(filename, data_class_name="Country")
        self.root_key = "3166-3"


class Scripts(pycountry.db.Database):
    """Provides access to an ISO 15924 database (Scripts)."""

    def __init__(self, filename: str) -> None:
        super().__init__(filename, data_class_name="Script")
        self.root_key = "15924"


class Currencies(pycountry.db.Database):
    """Provides access to an ISO 4217 database (Currencies)."""

    def __init__(self, filename: str) -> None:
        super().__init__(filename, data_class_name="Currency")
        self.root_key = "4217"


class Languages(pycountry.db.Database):
    """Provides access to an ISO 639-1/2T/3 database (Languages)."""

    no_index = ["status", "scope", "type", "inverted_name", "common_name"]

    def __init__(self, filename: str) -> None:
        super().__init__(filename, data_class_name="Language")
        self.root_key = "639-3"


class LanguageFamilies(pycountry.db.Database):
    """Provides access to an ISO 639-5 database
    (Language Families and Groups)."""

    def __init__(self, filename: str) -> None:
        super().__init__(filename, data_class_name="LanguageFamily")
        self.root_key = "639-5"


class Subdivision(pycountry.db.Data):
    def __init__(self, **kw):
        if "parent" in kw:
            kw["parent_code"] = kw["parent"]
        else:
            kw["parent_code"] = None
        super().__init__(**kw)
        self.country_code = self.code.split("-")[0]
        if self.parent_code is not None:
            self.parent_code = f"{self.country_code}-{self.parent_code}"

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
    # parent_code attribute is related to other subdivisions, *not*
    # the country!

    data_class_base = Subdivision
    data_class = pycountry.Subdivision
    no_index = ["name", "parent_code", "parent", "type"]
    root_key = "3166-2"

    def _load(self, *args, **kw):
        super()._load(*args, **kw)

        # Add index for the country code.
        self.indices["country_code"] = {}
        for subdivision in self:
            divs = self.indices["country_code"].setdefault(
                subdivision.country_code.lower(), set()
            )
            divs.add(subdivision)

    def get(self, **kw):
        default = kw.setdefault("default", None)
        subdivisions = super().get(**kw)
        if subdivisions is default and "country_code" in kw:
            # This handles the case where we know about a country but there
            # are no subdivisions: we return an empty list in this case
            # (sticking to the expected type here) instead of None.
            if countries.get(alpha_2=kw["country_code"]) is not None:
                return []
        return subdivisions


# Initialize instances with type hints
countries: ExistingCountries = ExistingCountries(
    os.path.join(DATABASE_DIR, "iso3166-1.json")
)
subdivisions: Subdivisions = Subdivisions(
    os.path.join(DATABASE_DIR, "iso3166-2.json")
)
historic_countries: HistoricCountries = HistoricCountries(
    os.path.join(DATABASE_DIR, "iso3166-3.json")
)

currencies: Currencies = Currencies(os.path.join(DATABASE_DIR, "iso4217.json"))

languages: Languages = Languages(os.path.join(DATABASE_DIR, "iso639-3.json"))
language_families: LanguageFamilies = LanguageFamilies(
    os.path.join(DATABASE_DIR, "iso639-5.json")
)

scripts: Scripts = Scripts(os.path.join(DATABASE_DIR, "iso15924.json"))
