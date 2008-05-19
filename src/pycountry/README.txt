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


Note that historic countries, defined by the ISO 3166-3 sub-standard are not
included in this list.
