"""Runtime contracts that the public annotations must continue to describe."""

import pytest

import pycountry
from pycountry import db


@pytest.mark.parametrize(
    "database, record_type",
    [
        (pycountry.countries, db.Country),
        (pycountry.historic_countries, db.Country),
        (pycountry.languages, db.Language),
        (pycountry.language_families, db.LanguageFamily),
        (pycountry.currencies, db.Currency),
        (pycountry.scripts, db.Script),
        (pycountry.subdivisions, pycountry.SubdivisionHierarchy),
    ],
)
def test_record_types(database, record_type):
    record = next(iter(database))
    assert isinstance(record, record_type)
    key = record.code if database is pycountry.subdivisions else record.name
    assert isinstance(database.lookup(key), record_type)


def test_subdivision_collection_return_types():
    subdivisions = pycountry.subdivisions
    german_subdivisions = subdivisions.get(country_code="DE")
    assert isinstance(german_subdivisions, set)
    assert subdivisions.lookup("DE") is german_subdivisions
    assert subdivisions.get(country_code="JE") == []
    assert isinstance(subdivisions.get(country_code="JE"), list)
    assert subdivisions.get(country_code="ZZ") is None
    fallback = object()
    assert subdivisions.get(country_code="ZZ", default=fallback) is fallback
    assert subdivisions.get(code="ZZ-01", default=fallback) is fallback


def test_subdivision_dictionary_can_contain_parent_record():
    subdivision = pycountry.subdivisions.get(code="FR-01")
    assert isinstance(
        dict(subdivision)["parent"], pycountry.SubdivisionHierarchy
    )


def test_annotations_do_not_supply_missing_attributes():
    aruba = pycountry.countries.lookup("AW")
    with pytest.raises(AttributeError):
        aruba.official_name
    assert getattr(aruba, "official_name", None) is None
    assert pycountry.subdivisions.get(code="DE-ST").parent_code is None


def test_remove_entry_ignores_custom_default():
    currencies = pycountry.Currencies(pycountry.currencies.filename)
    currencies.remove_entry(alpha_3="EUR", default=object())
    assert currencies.get(alpha_3="EUR") is None
    with pytest.raises(KeyError, match="not found"):
        currencies.remove_entry(alpha_3="EUR", default=object())
