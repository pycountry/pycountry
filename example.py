#!/usr/bin/env python3
"""
Example usage of the pyhscodes package.

This demonstrates how to use pyhscodes to work with Harmonized System codes
from the World Customs Organization.
"""

import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import pyhscodes


def main():
    print("=== pyhscodes Example ===")
    print()

    # Basic statistics
    print(f"Total HS codes: {len(pyhscodes.hscodes)}")
    print(f"Total sections: {len(pyhscodes.sections)}")
    print()

    # Working with sections
    print("=== Sections ===")
    for section in list(pyhscodes.sections)[:5]:  # Show first 5
        print(f"Section {section.section}: {section.name}")
    print("...")
    print()

    # Level breakdown
    print("=== HS Code Levels ===")
    print(f"Chapters (2-digit): {len(pyhscodes.hscodes.get_by_level('2'))}")
    print(f"Headings (4-digit): {len(pyhscodes.hscodes.get_by_level('4'))}")
    print(f"Subheadings (6-digit): {len(pyhscodes.hscodes.get_by_level('6'))}")
    print()

    # Get a specific code
    print("=== Specific Code Lookup ===")
    animals_chapter = pyhscodes.hscodes.get(hscode="01")
    if animals_chapter:
        print(f"Code: {animals_chapter.hscode}")
        print(f"Description: {animals_chapter.description}")
        print(f"Section: {animals_chapter.section}")
        print(f"Level: {animals_chapter.level}")
        print(f"Is Chapter: {animals_chapter.is_chapter}")
        print()

    # Get children of a code
    print("=== Children of Chapter 01 ===")
    children = pyhscodes.hscodes.get_children("01")
    for child in children:
        print(f"  {child.hscode}: {child.description}")
    print()

    # Get hierarchy for a specific code
    print("=== Hierarchy for Code 010121 ===")
    hierarchy = pyhscodes.hscodes.get_hierarchy("010121")
    for i, code in enumerate(hierarchy):
        indent = "  " * i
        print(f"{indent}{code.hscode}: {code.description} (Level {code.level})")
    print()

    # Fuzzy search
    print("=== Fuzzy Search Examples ===")

    # Search for horses
    print("Search for 'horses':")
    try:
        results = pyhscodes.hscodes.search_fuzzy("horses")
        for result in results[:3]:  # Show top 3
            print(f"  {result.hscode}: {result.description}")
    except LookupError:
        print("  No results found")
    print()

    # Search for dairy
    print("Search for 'dairy':")
    try:
        results = pyhscodes.hscodes.search_fuzzy("dairy")
        for result in results[:3]:  # Show top 3
            print(f"  {result.hscode}: {result.description}")
    except LookupError:
        print("  No results found")
    print()

    # Working with specific sections
    print("=== Working with Section I ===")
    section_i = pyhscodes.sections.get(section="I")
    if section_i:
        print(f"Section I: {section_i.name}")

        # Get all codes in section I
        section_i_codes = [code for code in pyhscodes.hscodes if code.section == "I"]
        print(f"Total codes in Section I: {len(section_i_codes)}")

        # Show chapters in section I
        chapters = [code for code in section_i_codes if code.is_chapter]
        print("Chapters in Section I:")
        for chapter in chapters:
            print(f"  {chapter.hscode}: {chapter.description}")


if __name__ == "__main__":
    main()
