"""Consumer checks, run by mypy; no database queries execute during testing."""

from typing import TypeVar

from typing_extensions import assert_type

import pycountry
from pycountry.db import (
    Country,
    Currency,
    Data,
    Database,
    Language,
    LanguageFamily,
    Script,
)

T = TypeVar("T", bound=Data)


def check_database(database: Database[T], record: T) -> None:
    assert_type(next(iter(database)), T)
    assert_type(database.lookup("value"), T)
    assert_type(database.get(name="value"), T | None)
    assert_type(database.get(name="value", default=None), T | None)
    assert_type(database.get(name="value", default=record), T)
    assert_type(database.get(name="value", default=False), T | bool)
    assert_type(database.get(name="value", default=0), T | int)
    assert_type(database.add_entry(name="value"), None)
    assert_type(database.remove_entry(name="value"), None)
    assert_type(database.remove_entry(name="value", default=object()), None)
    assert_type(database.factory, type[T])
    database.lookup(123)  # type: ignore[arg-type]
    database.get(name=123)  # type: ignore[call-overload]
    database.add_entry(name=123)  # type: ignore[arg-type]
    database.get(name="value").name  # type: ignore[union-attr]


def check_records() -> None:
    assert_type(pycountry.countries.get(alpha_2="DE"), Country | None)
    assert_type(
        pycountry.historic_countries.get(alpha_4="SUHH"), Country | None
    )
    assert_type(pycountry.languages.get(alpha_2="de"), Language | None)
    assert_type(
        pycountry.language_families.get(alpha_3="gem"), LanguageFamily | None
    )
    assert_type(pycountry.currencies.get(alpha_3="EUR"), Currency | None)
    assert_type(pycountry.scripts.get(alpha_4="Latn"), Script | None)

    country = pycountry.countries.lookup("DE")
    assert_type(country.alpha_2, str)
    assert_type(country.alpha_3, str)
    assert_type(country.flag, str)
    assert_type(country.official_name, str)
    assert_type(country.common_name, str)
    assert_type(dict(country), dict[str, str | Data | None])
    assert_type(
        pycountry.historic_countries.lookup("SUHH").withdrawal_date, str
    )
    assert_type(pycountry.languages.lookup("de").scope, str)
    assert_type(pycountry.languages.lookup("de").bibliographic, str)
    assert_type(pycountry.language_families.lookup("gem").alpha_3, str)
    assert_type(pycountry.currencies.lookup("EUR").numeric, str)
    assert_type(pycountry.scripts.lookup("Latn").alpha_4, str)
    assert_type(list(pycountry.currencies), list[Currency])
    assert_type(list(pycountry.languages), list[Language])
    assert_type(list(pycountry.language_families), list[LanguageFamily])
    assert_type(list(pycountry.scripts), list[Script])
    assert_type(pycountry.countries.search_fuzzy("England"), list[Country])
    assert_type(
        pycountry.historic_countries.search_fuzzy("Burma"), list[Country]
    )
    assert_type(pycountry.__version__, str)


def check_subdivisions() -> None:
    from pycountry import SubdivisionHierarchy

    assert_type(
        pycountry.subdivisions.get(code="DE-ST"), SubdivisionHierarchy | None
    )
    fallback = SubdivisionHierarchy(code="ZZ-01")
    assert_type(
        pycountry.subdivisions.get(code="ZZ-01", default=fallback),
        SubdivisionHierarchy,
    )
    assert_type(
        pycountry.subdivisions.get(code="ZZ-01", default=False),
        SubdivisionHierarchy | bool,
    )
    assert_type(
        pycountry.subdivisions.get(country_code="DE"),
        set[SubdivisionHierarchy] | list[SubdivisionHierarchy] | None,
    )
    assert_type(
        pycountry.subdivisions.get(country_code="ZZ", default=False),
        set[SubdivisionHierarchy] | list[SubdivisionHierarchy] | bool,
    )
    assert_type(
        pycountry.subdivisions.lookup("DE"),
        SubdivisionHierarchy | set[SubdivisionHierarchy],
    )
    assert_type(list(pycountry.subdivisions), list[SubdivisionHierarchy])
    assert_type(
        pycountry.subdivisions.match("Alabama"), list[SubdivisionHierarchy]
    )
    assert_type(
        pycountry.subdivisions.partial_match("Alabama"),
        list[SubdivisionHierarchy],
    )
    assert_type(
        pycountry.subdivisions.search_fuzzy("Alabama"),
        list[SubdivisionHierarchy],
    )
    subdivision = pycountry.subdivisions.get(code="DE-ST")
    if subdivision is not None:
        assert_type(subdivision.name, str)
        assert_type(subdivision.code, str)
        assert_type(subdivision.country, Country | None)
        assert_type(subdivision.parent, SubdivisionHierarchy | None)
        assert_type(subdivision.parent_code, str | None)
    pycountry.subdivisions.search_fuzzy(123)  # type: ignore[arg-type]
    pycountry.subdivisions.get(code="DE-ST").name  # type: ignore[union-attr]
