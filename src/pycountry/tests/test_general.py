import gettext
import pycountry
import pycountry.db
import pytest


@pytest.fixture(autouse=True, scope='session')
def logging():
    import logging
    logging.basicConfig(level=logging.DEBUG)


def test_country_list():
    assert len(pycountry.countries) == 249
    assert isinstance(list(pycountry.countries)[0], pycountry.db.Data)


def test_germany_has_all_attributes():
    germany = pycountry.countries.get(alpha2='DE')
    assert germany.alpha2 == u'DE'
    assert germany.alpha3 == u'DEU'
    assert germany.numeric == u'276'
    assert germany.name == u'Germany'
    assert germany.official_name == u'Federal Republic of Germany'


def test_subdivisions_directly_accessible():
    assert len(pycountry.subdivisions) == 4847
    assert isinstance(list(pycountry.subdivisions)[0], pycountry.db.Data)

    de_st = pycountry.subdivisions.get(code='DE-ST')
    assert de_st.code == u'DE-ST'
    assert de_st.name == u'Sachsen-Anhalt'
    assert de_st.type == u'State'
    assert de_st.country is pycountry.countries.get(alpha2='DE')


def test_subdivisions_have_subdivision_as_parent():
    al_br = pycountry.subdivisions.get(code='AL-BU')
    assert al_br.code == u'AL-BU'
    assert al_br.name == u'Bulqiz\xeb'
    assert al_br.type == u'District'
    assert al_br.parent_code == u'AL-09'
    assert al_br.parent is pycountry.subdivisions.get(code='AL-09')
    assert al_br.parent.name == u'Dib\xebr'


def test_query_subdivisions_of_country():
    assert len(pycountry.subdivisions.get(country_code='DE')) == 16
    assert len(pycountry.subdivisions.get(country_code='US')) == 57


def test_scripts():
    assert len(pycountry.scripts) == 169
    assert isinstance(list(pycountry.scripts)[0], pycountry.db.Data)

    latin = pycountry.scripts.get(name='Latin')
    assert latin.alpha4 == u'Latn'
    assert latin.name == u'Latin'
    assert latin.numeric == u'215'


def test_currencies():
    assert len(pycountry.currencies) == 182
    assert isinstance(list(pycountry.currencies)[0], pycountry.db.Data)

    argentine_peso = pycountry.currencies.get(letter='ARS')
    assert argentine_peso.letter == u'ARS'
    assert argentine_peso.name == u'Argentine Peso'
    assert argentine_peso.numeric == u'032'


def test_languages():
    assert len(pycountry.languages) == 487
    assert isinstance(list(pycountry.languages)[0], pycountry.db.Data)

    aragonese = pycountry.languages.get(alpha2='an')
    assert aragonese.alpha2 == u'an'
    assert aragonese.bibliographic == u'arg'
    assert aragonese.terminology == u'arg'
    assert aragonese.name == u'Aragonese'

    bengali = pycountry.languages.get(alpha2='bn')
    assert bengali.name == u'Bengali'
    assert bengali.common_name == u'Bangla'


def test_locales():
    german = gettext.translation(
        'iso3166', pycountry.LOCALES_DIR, languages=['de'])
    german.install()
    assert __builtins__['_']('Germany') == 'Deutschland'


def test_removed_countries():
    ussr = pycountry.historic_countries.get(alpha2='SU')
    assert isinstance(ussr, pycountry.db.Data)
    assert ussr.alpha4 == u'SUHH'
    assert ussr.alpha3 == u'SUN'
    assert ussr.name == u'USSR, Union of Soviet Socialist Republics'
    assert ussr.date_withdrawn == u'1992-08-30'
    assert ussr.deleted
    russia = pycountry.historic_countries.get(alpha2='RU')
    assert isinstance(russia, pycountry.db.Data)
    assert russia.name == u'Russian Federation'
    assert not russia.deleted
