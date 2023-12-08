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
