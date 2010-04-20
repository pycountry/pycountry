=========
pycountry
=========

pycountry provides the ISO databases for the standards:

639
  Languages

3166
  Countries

3166-2
  Subdivisions of countries

4217
  Currencies

15924
  Scripts

The package includes a copy from Debian's `pkg-isocodes` and makes the data
accessible through a Python API.

Translation files for the various strings are included as well.


Countries (ISO 3166)
====================

Countries are accessible through a database object that is already configured
upon import of pycountry and works as an iterable:

  >>> import pycountry
  >>> len(pycountry.countries)
  246
  >>> list(pycountry.countries)[0]
  <pycountry.db.Country object at 0x...>

Specific countries can be looked up by their various codes and provide the
information included in the standard as attributes:

  >>> germany = pycountry.countries.get(alpha2='DE')
  >>> germany
  <pycountry.db.Country object at 0x...>
  >>> germany.alpha2
  'DE'
  >>> germany.alpha3
  'DEU'
  >>> germany.numeric
  '276'
  >>> germany.name
  'Germany'
  >>> germany.official_name
  'Federal Republic of Germany'

Note that historic countries, defined by the ISO 3166-3 sub-standard are not
included in this list.

Country subdivisions (ISO 3166-2)
=================================

The country subdivisions are a little more complex than the countries itself
because they provide a nested and typed structure.

All subdivisons can be accessed directly:

  >>> len(pycountry.subdivisions)
  4548
  >>> list(pycountry.subdivisions)[0]
  <pycountry.db.Subdivision object at 0x...>

Subdivisions can be accessed using their unique code and provide at least
their code, name and type:

  >>> de_st= pycountry.subdivisions.get(code='DE-ST')
  >>> de_st.code
  'DE-ST'
  >>> de_st.name
  'Sachsen-Anhalt'
  >>> de_st.type
  'State'
  >>> de_st.country
  <pycountry.db.Country object at 0x...>

Some subdivisions specify another subdivision as a parent:

  >>> al_br = pycountry.subdivisions.get(code='AL-BU')
  >>> al_br.code
  'AL-BU'
  >>> al_br.name
  u'Bulqiz\xeb'
  >>> al_br.type
  'District'
  >>> al_br.parent_code
  'AL-09'
  >>> al_br.parent
  <pycountry.db.Subdivision object at 0x...>
  >>> al_br.parent.name
  u'Dib\xebr'

The divisions of a single country can be queried using the country_code index:

  >>> len(pycountry.subdivisions.get(country_code='DE'))
  16

  >>> len(pycountry.subdivisions.get(country_code='US'))
  57


Scripts (ISO 15924)
===================

Scripts are available from a database similar to the countries:

  >>> len(pycountry.scripts)
  146
  >>> list(pycountry.scripts)[0]
  <pycountry.db.Script object at 0x...>

  >>> latin = pycountry.scripts.get(name='Latin')
  >>> latin
  <pycountry.db.Script object at 0x...>
  >>> latin.alpha4
  'Latn'
  >>> latin.name
  'Latin'
  >>> latin.numeric
  '215'


Currencies (ISO 4217)
=====================

The currencies database is, again, similar to the ones before:

  >>> len(pycountry.currencies)
  182
  >>> list(pycountry.currencies)[0]
  <pycountry.db.Currency object at 0x...>

  >>> argentine_peso = pycountry.currencies.get(letter='ARS')
  >>> argentine_peso
  <pycountry.db.Currency object at 0x...>
  >>> argentine_peso.letter
  'ARS'
  >>> argentine_peso.name
  'Argentine Peso'
  >>> argentine_peso.numeric
  '032'


Languages (ISO 639)
===================

The languages database is similar too:

  >>> len(pycountry.languages)
  486
  >>> list(pycountry.languages)[0]
  <pycountry.db.Language object at 0x...>

  >>> aragonese = pycountry.languages.get(alpha2='an')
  >>> aragonese.alpha2
  'an'
  >>> aragonese.bibliographic
  'arg'
  >>> aragonese.terminology
  'arg'
  >>> aragonese.name
  'Aragonese'

Locales
=======

Locales are available in the `pycountry.LOCALES_DIR` subdirectory of this
package. The translation domains are called `isoXXX` according to the standard
they provide translations for. The directory is structured in a way compatible
to Python's gettext module.

Here is an example translating language names:

  >>> import gettext
  >>> german = gettext.translation('iso3166', pycountry.LOCALES_DIR,
  ...                              languages=['de'])
  >>> german.install()
  >>> _('Germany')
  'Deutschland'
