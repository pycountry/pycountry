"""pyhscodes - Harmonized System codes from the World Customs Organization"""

import os.path
import unicodedata
from importlib import metadata as _importlib_metadata
from typing import Dict, List, Optional, Type

import pyhscodes.db

# We prioritise importing the backported `importlib_resources`
# because the function we use (`importlib.resources.files`) is only
# available from Python 3.9, but the module itself exists since 3.7.
# We install `importlib_resources` on Python < 3.9.
# TODO: Remove usage of importlib_resources once support for Python 3.8 is dropped
try:
    import importlib_resources  # type: ignore
except ModuleNotFoundError:
    from importlib import resources as importlib_resources  # type: ignore


def resource_filename(package_or_requirement: str, resource_name: str) -> str:
    return str(importlib_resources.files(package_or_requirement) / resource_name)


def get_version(distribution_name: str) -> Optional[str]:
    try:
        return _importlib_metadata.version(distribution_name)
    except _importlib_metadata.PackageNotFoundError:
        return "n/a"


# Variable annotations
DATABASE_DIR: str = resource_filename("pyhscodes", "databases")
__version__: Optional[str] = get_version("pyhscodes")


def remove_accents(input_str: str) -> str:
    output_str = input_str
    if not input_str.isascii():
        # Borrowed from https://stackoverflow.com/a/517974/1509718
        nfkd_form = unicodedata.normalize("NFKD", input_str)
        output_str = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return output_str


class HSCodes(pyhscodes.db.Database):
    """Provides access to Harmonized System codes database."""

    data_class = pyhscodes.db.HSCode
    root_key = "hscodes"

    def search_fuzzy(self, query: str) -> List[Type["HSCodes"]]:
        query = remove_accents(query.strip().lower())

        # A code to points mapping for later sorting codes
        # based on the query's matching incidence.
        results: dict[str, int] = {}

        def add_result(hscode: "pyhscodes.db.HSCode", points: int) -> None:
            results.setdefault(hscode.hscode, 0)
            results[hscode.hscode] += points

        # Prio 1: exact matches on HS code numbers
        try:
            add_result(self.lookup(query), 50)
        except LookupError:
            pass

        # Prio 2: exact matches on descriptions
        try:
            result = self.get(description=query)
            if result is not None:
                add_result(result, 49)
        except (LookupError, TypeError):
            pass

        # Prio 3: partial matches on descriptions
        for candidate in self:
            description = candidate._fields.get("description")
            if description is not None:
                description = remove_accents(description.lower())
                if query in description:
                    # This prefers codes with a match early in their description
                    add_result(candidate, max([5, 30 - (2 * description.find(query))]))

        if not results:
            raise LookupError(query)

        sorted_results = [
            self.get(hscode=x[0])
            # sort by points first, by hscode second
            for x in sorted(results.items(), key=lambda x: (-x[1], x[0]))
        ]
        return sorted_results

    def get_by_level(self, level: str) -> List[pyhscodes.db.HSCode]:
        """Get all HS codes at a specific level (2, 4, or 6)."""
        return [obj for obj in self if obj.level == level]

    def get_children(self, parent_code: str) -> List[pyhscodes.db.HSCode]:
        """Get all child codes for a given parent code."""
        return [obj for obj in self if obj.parent == parent_code]

    def get_hierarchy(self, hscode: str) -> List[pyhscodes.db.HSCode]:
        """Get the full hierarchy path for a given HS code."""
        hierarchy = []
        current = self.get(hscode=hscode)

        while current:
            hierarchy.insert(0, current)
            if current.parent and current.parent != "TOTAL":
                current = self.get(hscode=current.parent)
            else:
                break

        return hierarchy


class Sections(pyhscodes.db.Database):
    """Provides access to HS code sections database."""

    data_class = pyhscodes.db.Section
    root_key = "sections"


# Create database instances
hscodes = HSCodes(os.path.join(DATABASE_DIR, "hscodes.json"))
sections = Sections(os.path.join(DATABASE_DIR, "sections.json"))
