import os.path

import pycountry


def test_add_entry():
    pycountry.countries._clear()
    assert pycountry.countries.get(alpha_2="XK") is None

    pycountry.countries.add_entry(
        alpha_2="XK", alpha_3="XXK", name="Kosovo", numeric="926"
    )

    country = pycountry.countries.get(alpha_2="XK")
    assert isinstance(country, pycountry.countries.data_class)


def test_remove_entry():
    pycountry.countries._clear()
    assert pycountry.countries.get(alpha_2="DE") is not None

    pycountry.countries.remove_entry(alpha_2="DE")

    assert pycountry.countries.get(alpha_2="DE") is None


def test_no_results_lookup_error():
    try:
        import importlib_resources
    except ModuleNotFoundError:
        from importlib import resources as importlib_resources

    def resource_filename(package_or_requirement, resource_name):
        return str(
            importlib_resources.files(package_or_requirement) / resource_name
        )

    DATABASE_DIR = resource_filename("pycountry", "databases")
    countries = pycountry.ExistingCountries(
        os.path.join(DATABASE_DIR, "iso3166-1.json")
    )

    query = "nonexistent query"
    with pytest.raises(LookupError):
        countries.search_fuzzy(query)
