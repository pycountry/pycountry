pycountry
=========

.. image:: https://img.shields.io/pypi/v/pycountry.svg
    :target: https://pypi.org/project/pycountry/
    :alt: PyPI Version

``pycountry`` is a Python library offering a convenient way to access various standardized lists and codes from around the world. Whether you need to work with language names, country codes, currency information, or scripts, ``pycountry`` has you covered. It's a go-to solution for developers needing to handle international data, as it provides an extensive collection of data sets based on widely recognized International Standards Organization (ISO) standards.

These standards are used globally for consistent representation of critical information, such as the standardized names of countries (`3166 <https://en.wikipedia.org/wiki/ISO_3166>`_), languages (`639-3 <https://en.wikipedia.org/wiki/ISO_639-3>`_), and currencies (`4217 <https://en.wikipedia.org/wiki/ISO_4217>`_). With pycountry, this wealth of information is easily accessible through a simple Python interface, making it an invaluable tool for internationalization and localization in software development.

``pycountry`` supports the following ISO databases for their standards:

* `639-3 <https://en.wikipedia.org/wiki/ISO_639-3>`_ | `Languages (ISO 639-3)`_
* `3166 <https://en.wikipedia.org/wiki/ISO_3166>`_ | Codes for representation of names of countries and their subdivisions
  * `3166-1 <https://en.wikipedia.org/wiki/ISO_3166-1>`_ | `Countries (ISO 3166-1)`_
  * `3166-3 <https://en.wikipedia.org/wiki/ISO_3166-3>`_ | `Historic Countries (ISO 3166-3)`_
  * `3166-2 <https://en.wikipedia.org/wiki/ISO_3166-2>`_ | `Country Subdivisions (ISO 3166-2)`_
* `4217 <https://en.wikipedia.org/wiki/ISO_4217>`_ | `Currencies (ISO 4217)`_
* `15924 <https://en.wikipedia.org/wiki/ISO_15924>`_ | `Scripts (ISO 15924)`_

The package includes a copy from Debian's `pkg-isocodes <https://salsa.debian.org/iso-codes-team/iso-codes>`_, utilizing this data under the GNU Lesser General Public License Version 2.1. This ensures that pycountry's users have access to reliable and regularly updated international standards.

Additionally, ``pycountry`` provides translations for various strings, facilitated by the use of the `gettext` library. This feature enhances the library's utility in multilingual applications and environments.

Table of Contents
================

.. contents::
   :local:
   :depth: 2

Data update policy
------------------

``pycountry`` is a wrapper around the ISO standards, using the Debian's `pkg-isocodes <https://salsa.debian.org/iso-codes-team/iso-codes>`_ database as is. We do not make changes to the data.

To update data from Debian, run ``make`` in the base directory. For amendments to the data provided by Debian please reach out to them.

For custom local modifications, see the `Custom Countries`_ section.

Donations / Monetary Support
----------------------------

``pycountry`` is maintained by volunteers. We suggest supporting `Feminist Frequency <https://feministfrequency.com/donate/>`_ as a way to contribute to the project's spirit. Share your support to inspire others!

Contributions
-------------

The code lives in a `git repository on GitHub <https://github.com/pycountry/pycountry>`_, and issues must be reported in there as well. Please follow the provided Pull Request template.

Installation
------------

Installing ``pycountry`` is simple and straightforward. You can install it directly from the Python Package Index (PyPI) using `pip`, a package manager for Python that simplifies the process of installing and managing Python libraries.

To install ``pycountry``, open your terminal and run the following command:

.. code:: pycon

  pip install pycountry

This command will download and install the latest version of ``pycountry`` along with its dependencies. Ensure that you have pip installed and up to date before running this command.

Requirements
^^^^^^^^^^^^

* Python 3.8 or newer
* Internet connection to download the package from PyPI.

After the installation is complete, you can start using ``pycountry`` in your Python projects to access ISO country, language, currency, and script data.

For more detailed information about ``pycountry`` and its usage, refer to the `Documentation`_ section of this document.

PyInstaller Compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^

Some users have reported issues using ``pycountry`` with PyInstaller guidance on how to handle the issues can be found in the `PyInstaller Google Group <https://groups.google.com/g/pyinstaller/c/OYhJdeZ9010/m/vLhYAWUzAQAJ>`_.

Documentation
-------------

Countries (ISO 3166-1)
^^^^^^^^^^^^^^^^^^^^^^

Countries in ``pycountry`` store comprehensive data on each country per the `3166-1 <https://en.wikipedia.org/wiki/ISO_3166-1>`_ standard. You can iterate through all countries, look up specific countries using various codes, and perform fuzzy searches.

Countries are accessible through a database object that is already configured upon import of ``pycountry`` and works as an iterable:

.. code:: pycon

  >>> import pycountry
  >>> len(pycountry.countries)
  249
  >>> list(pycountry.countries)[0]
  Country(alpha_2='AF', alpha_3='AFG', name='Afghanistan', numeric='004', official_name='Islamic Republic of Afghanistan')

Specific countries can be looked up by their various codes and provide the information included in the standard as attributes:

.. code:: pycon

  >>> germany = pycountry.countries.get(alpha_2='DE')
  >>> germany
  Country(alpha_2='DE', alpha_3='DEU', name='Germany', numeric='276', official_name='Federal Republic of Germany')
  >>> germany.alpha_2
  'DE'
  >>> germany.alpha_3
  'DEU'
  >>> germany.numeric
  '276'
  >>> germany.name
  'Germany'
  >>> germany.official_name
  'Federal Republic of Germany'

There's also a "fuzzy" search to help people discover "proper" countries for names that might only actually be subdivisions. The fuzziness also includes normalizing unicode accents. There's also a bit of prioritization included to prefer matches on country names before subdivision names and have countries with more matches be listed before ones with fewer matches:

.. code:: pycon

  >>> pycountry.countries.search_fuzzy('England')
  [Country(alpha_2='GB', alpha_3='GBR', name='United Kingdom', numeric='826', official_name='United Kingdom of Great Britain and Northern Ireland')]

  >>> pycountry.countries.search_fuzzy('Cote')
  [Country(alpha_2='CI', alpha_3='CIV', name="Côte d'Ivoire", numeric='384', official_name="Republic of Côte d'Ivoire"),
   Country(alpha_2='FR', alpha_3='FRA', name='France', numeric='250', official_name='French Republic'),
   Country(alpha_2='HN', alpha_3='HND', name='Honduras', numeric='340', official_name='Republic of Honduras')]

Attributes for the country class can be accessed using the ``__getattr__`` method. If the requested attribute is a key for the country class, it will return the corresponding value. In the special cases of missing 'common_name' or 'official_name' attributes, ``__getattr__`` will return 'name'. Here are some examples:

.. code:: pycon

  >>> aland = pycountry.countries.get(alpha_2='AX')

  >>> print(aland)
  Country(alpha_2='AX', alpha_3='ALA', flag='🇦🇽', name='Åland Islands', numeric='248')

  >>> aland.common_name
  UserWarning: Country's common_name not found. Country name provided instead.
    warnings.warn(warning_message, UserWarning)
  'Åland Islands'

  >>> aland.official_name
  Country's official_name not found. Country name provided instead.
    warnings.warn(warning_message, UserWarning)
  'Åland Islands'

  >>> aland.flag
  '🇦🇽'

  >>> aland.foo  # Raises AttributeError

Historic Countries (ISO 3166-3)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section includes former countries as per `3166-3 <https://en.wikipedia.org/wiki/ISO_3166-3>`_. These are countries that have been dissolved but are still relevant historically.

The `historic_countries` database contains former countries that have been removed from the standard and are now included in ISO 3166-3, excluding existing ones:

.. code:: pycon

 >>> ussr = pycountry.historic_countries.get(alpha_3='SUN')
 >>> ussr
 Country(alpha_3='SUN', alpha_4='SUHH', withdrawal_date='1992-08-30', name='USSR, Union of Soviet Socialist Republics', numeric='810')
 >>> ussr.alpha_4
 'SUHH'
 >>> ussr.alpha_3
 'SUN'
 >>> ussr.name
 'USSR, Union of Soviet Socialist Republics'
 >>> ussr.withdrawal_date
 '1992-08-30'


Country Subdivisions (ISO 3166-2)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Subdivisions in ``pycountry`` provide detailed data about country divisions, such as states, provinces, and other administrative regions as per `3166-2 <https://en.wikipedia.org/wiki/ISO_3166-2>`_.

The country ``subdivisions`` are a little more complex than the ``countries`` because they are in a nested structure.

All subdivisons can be accessed directly:

.. code:: pycon

  >>> len(pycountry.subdivisions)
  4847
  >>> list(pycountry.subdivisions)[0]
  Subdivision(code='AD-07', country_code='AD', name='Andorra la Vella', parent_code=None, type='Parish')

Subdivisions can be accessed using their unique code. The resulting object will provide at least their code, name and type:

.. code:: pycon

  >>> de_st = pycountry.subdivisions.get(code='DE-ST')
  >>> de_st.code
  'DE-ST'
  >>> de_st.name
  'Sachsen-Anhalt'
  >>> de_st.type
  'State'
  >>> de_st.country
  Country(alpha_2='DE', alpha_3='DEU', name='Germany', numeric='276', official_name='Federal Republic of Germany')

Some subdivisions specify another subdivision as a parent:

.. code:: pycon

  >>> al_br = pycountry.subdivisions.get(code='AL-BU')
  >>> al_br.code
  'AL-BU'
  >>> al_br.name
  'Bulqiz\xeb'
  >>> al_br.type
  'District'
  >>> al_br.parent_code
  'AL-09'
  >>> al_br.parent
  Subdivision(code='AL-09', country_code='AL', name='Dib\xebr', parent_code=None, type='County')
  >>> al_br.parent.name
  'Dib\xebr'

The divisions of a single country can be queried using the country_code index:

.. code:: pycon

  >>> len(pycountry.subdivisions.get(country_code='DE'))
  16

  >>> len(pycountry.subdivisions.get(country_code='US'))
  57

Similar to countries, the `search_fuzzy` method has been implemented for subdivisions to facilitate finding relevant subdivision entries. This method includes unicode normalization for accents and prioritizes matches on subdivision names. The search algorithm is designed to return more relevant matches first:

This method is especially useful for cases where the exact name or code of the subdivision is not known.

.. code:: pycon

  >>> pycountry.subdivisions.search_fuzzy('York')
    [Subdivision(code='GB-YOR', country_code='GB', name='York', parent='GB-ENG', parent_code='GB-GB-ENG', type='Unitary authority')
    Subdivision(code='GB-ERY', country_code='GB', name='East Riding of Yorkshire', parent='GB-ENG', parent_code='GB-GB-ENG', type='Unitary authority')
    Subdivision(code='GB-NYK', country_code='GB', name='North Yorkshire', parent='GB-ENG', parent_code='GB-GB-ENG', type='Two-tier county')
    Subdivision(code='US-NY', country_code='US', name='New York', parent_code=None, type='State')]

Scripts (ISO 15924)
^^^^^^^^^^^^^^^^^^^

Access script information based on `15924 <https://en.wikipedia.org/wiki/ISO_15924>`_, useful for applications dealing with linguistic and cultural data. Scripts are available from a database similar to the countries:

.. code:: pycon

  >>> len(pycountry.scripts)
  169
  >>> list(pycountry.scripts)[0]
  Script(alpha_4='Afak', name='Afaka', numeric='439')

  >>> latin = pycountry.scripts.get(name='Latin')
  >>> latin
  Script(alpha_4='Latn', name='Latin', numeric='215')
  >>> latin.alpha4
  'Latn'
  >>> latin.name
  'Latin'
  >>> latin.numeric
  '215'


Currencies (ISO 4217)
^^^^^^^^^^^^^^^^^^^^^

Access currency infromation based on `4217 <https://en.wikipedia.org/wiki/ISO_4217>`_, including currency names and codes. The currencies database is, again, similar to the ones before:

.. code:: pycon

  >>> len(pycountry.currencies)
  182
  >>> list(pycountry.currencies)[0]
  Currency(alpha_3='AED', name='UAE Dirham', numeric='784')
  >>> argentine_peso = pycountry.currencies.get(alpha_3='ARS')
  >>> argentine_peso
  Currency(alpha_3='ARS', name='Argentine Peso', numeric='032')
  >>> argentine_peso.alpha_3
  'ARS'
  >>> argentine_peso.name
  'Argentine Peso'
  >>> argentine_peso.numeric
  '032'


Languages (ISO 639-3)
^^^^^^^^^^^^^^^^^^^^^

The language database in ``pycountry`` covers a wide range of languages as per `639-3 <https://en.wikipedia.org/wiki/ISO_639-3>`_. This is particularly useful for multilingual applications.

.. code:: pycon

  >>> len(pycountry.languages)
  7874
  >>> list(pycountry.languages)[0]
  Language(alpha_3='aaa', name='Ghotuo', scope='I', type='L')

  >>> aragonese = pycountry.languages.get(alpha_2='an')
  >>> aragonese.alpha_2
  'an'
  >>> aragonese.alpha_3
  'arg'
  >>> aragonese.name
  'Aragonese'

  >>> bengali = pycountry.languages.get(alpha_2='bn')
  >>> bengali.name
  'Bengali'
  >>> bengali.common_name
  'Bangla'

Locales
^^^^^^^

``pycountry`` provides locale support, compatible with Python's gettext module, enabling easy translation of country names and other data.


Locales are available in the ``pycountry.LOCALES_DIR`` subdirectory of this package. The translation domains are called ``isoXXX`` according to the standard they provide translations for. The directory is structured in a way compatible to Python's gettext module.

Here is an example translating language names:

.. code:: pycon

  >>> import gettext
  >>> german = gettext.translation('iso3166-1', pycountry.LOCALES_DIR,
  ...                              languages=['de'])
  >>> german.install()
  >>> _('Germany')
  'Deutschland'


Lookups
^^^^^^^

You can perform case-insensitive lookups for countries, languages, and other data without knowing the exact key to match.

The search will end once the first match is found, which is returned. This can sometimes result in unexpected or unintuitive returns.

.. code:: pycon

  >>> pycountry.countries.lookup('de')
  <pycountry.db.Country object at 0x...>

The search ends with the first match, which is returned.


Dict Compatibility
^^^^^^^^^^^^^^^^^^

All ``pycountry`` objects can be cast to dictionaries for ease of use and integration with other Python data structures.

.. code:: pycon

 >>> country = pycountry.countries.lookup('de')
 >>> dict(country)
 {'alpha_2': 'DE', 'name': 'Germany', ...}


Custom Countries
^^^^^^^^^^^^^^^^

While ``pycountry`` adheres to ISO standards, it also allows runtime modifications like adding or removing entries to suit specific needs.

Add a non-ISO country:

.. code:: pycon

 >>> pycountry.countries.add_entry(alpha_2="XK", alpha_3="XXK", name="Kosovo", numeric="926")

Remove a country from a database:

.. code:: pycon

 >>> pycountry.countries.remove_entry(alpha_2="XK")

Contributing
------------

We welcome contributions to ``pycountry``! Whether it's improving documentation, adding new features, or fixing bugs, your contributions are greatly appreciated.

To get started:

#. Fork the repository on GitHub.
#. Clone your fork locally using ``git clone <your-fork-url>``.
#. Navigate to the cloned directory: ``cd pycountry``.
#. Install the project and its dependencies: ``pip install -e .`` (This installs the package in editable mode).
#. Create a new feature branch: ``git checkout -b my-new-feature``.
#. Make your changes and commit them: ``git commit -am 'Add some feature'``.
#. Push the branch to GitHub: ``git push origin my-new-feature``.
#. Submit a pull request through the GitHub website.

Please ensure your code adheres to the project's coding standards and includes appropriate tests. Additionally, update or add documentation as necessary. For more detailed information, refer to our `CONTRIBUTING <https://github.com/pycountry/pycountry/blob/main/CONTRIBUTING.md>`_ file.

Running Tests
-------------

To maintain the quality of ``pycountry``, we encourage contributors to run tests and perform code quality checks before submitting any changes. ``pycountry`` uses Poetry for dependency management and tools like ``mypy``, ``pre-commit``, and ``make`` for testing and linting.

To run the test suite:

#. Install Poetry if you haven't already. Visit the Poetry website for `installation instructions <https://python-poetry.org/docs/#installation>`_.
#. Install the project dependencies by running ``poetry install`` in the project's root directory. This command also installs necessary tools like ``mypy`` and ``pre-commit`` as defined in ``pyproject.toml``.
#. Activate the Poetry shell with ``poetry shell``. This will spawn a new shell subprocess, which is configured to use your project’s virtual environment.
#. Run the unit tests, linting checks, and type checks using ``make check``. Ensure you have `make` installed on your system (commonly pre-installed on Unix-like systems).
#. Ensure all tests pass successfully.

If you add new features or fix bugs, please include corresponding tests. Follow the project's coding standards and update documentation as needed.

Note: The project's dependencies and the environment needed to run tests are managed by Poetry, using the ``pyproject.toml`` and ``poetry.lock`` files.

License
-------

``pycountry`` is made available under the GNU Lesser General Public License Version 2.1 (LGPL 2.1). This license allows you to use, modify, and distribute the library in your own projects.

For more details, see the `LICENSE <https://github.com/pycountry/pycountry/blob/main/LICENSE.txt>`_ file included with the source code.

Credits
-------

``pycountry`` is developed and maintained by a community of developers and contributors. Special thanks to everyone who has contributed their time and effort.
We gratefully acknowledge the Debian `pkg iso-codes <https://salsa.debian.org/iso-codes-team/iso-codes>`_ team and contributors for their work and for making this resource freely available.

For a complete list of contributors, see the `COPYRIGHT <https://github.com/pycountry/pycountry/blob/main/COPYRIGHT.txt>`_ file.

Acknowledgments
----------------

We would like to express our gratitude to the authors and maintainers of the following libraries, which have greatly contributed to the functionality and internationalization of ``pycountry``:

* `country-info <https://github.com/countryinfo/countryinfo>`_
* `babel <https://github.com/python-babel/babel>`_

These libraries provide valuable data and localization support that complement the features of ``pycountry``.

Maintainers
-----------

* `Christian Theune <https://github.com/ctheune>`_
* `Nate Schimmoller <https://github.com/nschimmoller>`_
* `Zachary Ware <https://github.com/zware>`_
