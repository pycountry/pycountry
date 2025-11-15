"""pycountry"""

import os.path
import unicodedata
from importlib import metadata as _importlib_metadata
from importlib import resources as _importlib_resources
from typing import Any, Optional, Union

import pycountry.db


def resource_filename(package_or_requirement: str, resource_name: str) -> str:
    return str(
        _importlib_resources.files(package_or_requirement) / resource_name
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


class ExistingCountries(pycountry.db.Database):
    """Provides access to an ISO 3166 database (Countries)."""

    data_class = pycountry.db.Country
    root_key = "3166-1"

    def search_fuzzy(self, query: str) -> list[pycountry.db.Country]:
        query = remove_accents(query.strip().lower())

        # A country-code to points mapping for later sorting countries
        # based on the query's matching incidence.
        results: dict[str, int] = {}

        def add_result(country: "pycountry.db.Country", points: int) -> None:
            results.setdefault(country.alpha_2, 0)
            results[country.alpha_2] += points

        # Prio 1: exact matches on country names
        try:
            country = self.lookup(query)
            if isinstance(country, pycountry.db.Country):
                add_result(country, 50)
        except LookupError:
            pass

        # Prio 2: exact matches on subdivision names
        match_subdivions = subdivisions.match(query)
        for candidate in match_subdivions:
            country_result = candidate.country
            if isinstance(country_result, pycountry.db.Country):
                add_result(country_result, 49)

        # Prio 3: partial matches on country names
        for candidate_data in self:
            if isinstance(candidate_data, pycountry.db.Country):
                # Higher priority for a match on the common name
                for v in [
                    candidate_data._fields.get("name"),
                    candidate_data._fields.get("official_name"),
                    candidate_data._fields.get("comment"),
                ]:
                    if v is not None:
                        # Check for initials match
                        initials = "".join([c for c in v if c.isupper()])
                        if query == remove_accents(initials.lower()):
                            add_result(candidate_data, 40)
                            break
                        v_normalized = remove_accents(v.lower())
                        if query in v_normalized:
                            # This prefers countries with a match early in
                            # their name and also balances against countries
                            # with a number of partial matches and their name
                            # containing 'new' in the middle
                            add_result(
                                candidate_data,
                                max(
                                    [
                                        5,
                                        30 - (2 * v_normalized.find(query)),
                                    ]
                                ),
                            )
                            break

        # Prio 4: partial matches on subdivision names
        partial_match_subdivisions = subdivisions.partial_match(query)
        for candidate in partial_match_subdivisions:
            name = candidate._fields.get("name")
            if name is not None:
                name_normalized = remove_accents(name.lower())
                if query in name_normalized:
                    country_result = candidate.country
                    if isinstance(country_result, pycountry.db.Country):
                        add_result(
                            country_result,
                            max([1, 5 - name_normalized.find(query)]),
                        )

        if not results:
            raise LookupError(query)

        sorted_results: list[pycountry.db.Country] = []
        for x in sorted(results.items(), key=lambda x: (-x[1], x[0])):
            country_data: Optional[pycountry.db.Data] = self.get(alpha_2=x[0])
            if isinstance(country_data, pycountry.db.Country):
                sorted_results.append(country_data)
        return sorted_results


class HistoricCountries(ExistingCountries):
    """Provides access to an ISO 3166-3 database
    (Countries that have been removed from the standard)."""

    data_class = pycountry.db.Country
    root_key = "3166-3"


class Scripts(pycountry.db.Database):
    """Provides access to an ISO 15924 database (Scripts)."""

    data_class = "Script"
    root_key = "15924"


class Currencies(pycountry.db.Database):
    """Provides access to an ISO 4217 database (Currencies)."""

    data_class = "Currency"
    root_key = "4217"


class Languages(pycountry.db.Database):
    """Provides access to an ISO 639-1/2T/3 database (Languages)."""

    no_index = ["status", "scope", "type", "inverted_name", "common_name"]

    data_class = "Language"
    root_key = "639-3"


class LanguageFamilies(pycountry.db.Database):
    """Provides access to an ISO 639-5 database
    (Language Families and Groups)."""

    data_class = "LanguageFamily"
    root_key = "639-5"


class SubdivisionHierarchy(pycountry.db.Data):
    def __init__(self, **kw: str) -> None:
        parent_code: Optional[str] = None
        if "parent" in kw:
            parent_code = kw["parent"]
            kw["parent_code"] = kw["parent"]
        else:
            # Don't set parent_code if not provided - let it be None
            if "parent_code" not in kw:
                kw["parent_code"] = None  # type: ignore[assignment]
        super().__init__(**kw)
        self.country_code = self.code.split("-")[0]
        if parent_code is not None:
            # Split the parent_code to check if the country_code is already
            # present
            parts = parent_code.split("-")
            if parts[0] != self.country_code:
                self.parent_code = f"{self.country_code}-{parent_code}"

    @property
    def country(self) -> Optional[pycountry.db.Country]:
        result: Optional[pycountry.db.Data] = countries.get(
            alpha_2=self.country_code
        )
        if isinstance(result, pycountry.db.Country):
            return result
        return None

    @property
    def parent(self) -> Optional["SubdivisionHierarchy"]:
        if not self.parent_code:
            return None
        result = subdivisions.get(code=self.parent_code)
        if isinstance(result, SubdivisionHierarchy):
            return result
        return None


class Subdivisions(pycountry.db.Database):
    # Note: subdivisions can be hierarchical to other subdivisions. The
    # parent_code attribute is related to other subdivisions, *not*
    # the country!

    data_class = SubdivisionHierarchy
    no_index = ["name", "parent_code", "parent", "type"]
    root_key = "3166-2"

    def _load(self, *args: Any, **kw: Any) -> None:
        super()._load(*args, **kw)

        # Add index for the country code.
        country_code_index: dict[str, set[SubdivisionHierarchy]] = {}
        for subdivision in self:
            if isinstance(subdivision, SubdivisionHierarchy):
                divs = country_code_index.setdefault(
                    subdivision.country_code.lower(),
                    set(),
                )
                divs.add(subdivision)
        # Type ignore needed because indices is typed as dict[str, Data]
        # but we're storing sets here
        self.indices["country_code"] = country_code_index  # type: ignore[assignment]

    def get(  # type: ignore[override]
        self, *, default: Optional[SubdivisionHierarchy] = None, **kw: str
    ) -> Union[Optional[SubdivisionHierarchy], list[SubdivisionHierarchy]]:
        popped_default = kw.pop("default", None)
        if popped_default is None:
            default_val: Optional[SubdivisionHierarchy] = default
        elif isinstance(popped_default, SubdivisionHierarchy):
            default_val = popped_default
        else:
            default_val = default
        result: Optional[pycountry.db.Data] = super().get(**kw)  # type: ignore[arg-type]
        if result is None and "country_code" in kw:
            # This handles the case where we know about a country but there
            # are no subdivisions: we return an empty list in this case
            # (sticking to the expected type here) instead of None.
            country_code = kw["country_code"]
            country_result: Optional[pycountry.db.Data] = countries.get(
                alpha_2=country_code
            )
            if country_result is not None:
                return []
        # Convert set to list for consistency when querying by country_code
        if "country_code" in kw:
            country_code_index = self.indices.get("country_code", {})
            if isinstance(country_code_index, dict):
                country_code_lower = kw["country_code"].lower()
                if country_code_lower in country_code_index:
                    divs = country_code_index[country_code_lower]
                    if isinstance(divs, set):
                        return list(divs)
        if isinstance(result, SubdivisionHierarchy):
            return result
        return default_val

    def match(self, query: str) -> list[SubdivisionHierarchy]:
        query = remove_accents(query.strip().lower())
        matching_candidates: list[SubdivisionHierarchy] = []
        for candidate in self:
            if isinstance(candidate, SubdivisionHierarchy):
                for v in candidate._fields.values():
                    if v is not None:
                        v_normalized = remove_accents(v.lower())
                        # Some names include alternative versions which we want to
                        # match exactly.
                        for w in v_normalized.split(";"):
                            if w == query:
                                matching_candidates.append(candidate)
                                break

        return matching_candidates

    def partial_match(self, query: str) -> list[SubdivisionHierarchy]:
        query = remove_accents(query.strip().lower())
        matching_candidates: list[SubdivisionHierarchy] = []
        for candidate in self:
            if isinstance(candidate, SubdivisionHierarchy):
                name = candidate._fields.get("name")
                if name is not None:
                    name_normalized = remove_accents(name.lower())
                    if query in name_normalized:
                        matching_candidates.append(candidate)

        return matching_candidates

    def search_fuzzy(self, query: str) -> list[SubdivisionHierarchy]:
        query = remove_accents(query.strip().lower())

        # A Subdivision's code to points mapping for later sorting subdivisions
        # based on the query's matching incidence.
        results: dict[str, int] = {}

        def add_result(subdivision: SubdivisionHierarchy, points: int) -> None:
            results.setdefault(subdivision.code, 0)
            results[subdivision.code] += points

        # Prio 1: exact matches on subdivision names
        match_subdivisions = self.match(query)
        for candidate in match_subdivisions:
            add_result(candidate, 50)

        # Prio 2: partial matches on subdivision names
        partial_match_subdivisions = self.partial_match(query)
        for candidate in partial_match_subdivisions:
            name = candidate._fields.get("name")
            if name is not None:
                name_normalized = remove_accents(name.lower())
                if query in name_normalized:
                    add_result(
                        candidate,
                        max([1, 5 - name_normalized.find(query)]),
                    )

        if not results:
            raise LookupError(query)

        sorted_results: list[SubdivisionHierarchy] = []
        for x in sorted(results.items(), key=lambda x: (-x[1], x[0])):
            result = self.get(code=x[0])
            if isinstance(result, SubdivisionHierarchy):
                sorted_results.append(result)
        return sorted_results


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
