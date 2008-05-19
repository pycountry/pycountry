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

The databases are imported from Debian's `pkg-isocodes` and made accessible
through a Python API.

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


Scripts (ISO 15924)
===================

Scripts are available from a database similar to the countries:

  >>> len(pycountry.scripts)
  131
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
  183
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
