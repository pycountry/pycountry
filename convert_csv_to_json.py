#!/usr/bin/env python3
"""
Convert HS codes and sections CSV data to JSON format for pyhscodes database.

This script expects two CSV files:
1. harmonized-system.csv with columns: section,hscode,description,parent,level
2. sections.csv with columns: section,name

It will generate:
1. src/pyhscodes/databases/hscodes.json
2. src/pyhscodes/databases/sections.json
"""

import csv
import json
import os
from pathlib import Path

# TODO: ensure script finds and updates entries rather than overwriting them so that we don't lose standards and commodity information
def convert_hscodes_csv_to_json(csv_file: str, json_file: str):
    """Convert HS codes CSV to JSON format."""
    hscodes = []

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hscode_entry = {
                "section": row["section"],
                "hscode": row["hscode"],
                "description": row["description"],
                "parent": row["parent"],
                "level": row["level"],
            }
            hscodes.append(hscode_entry)

    # Create the JSON structure expected by the database
    json_data = {"hscodes": hscodes}

    # Ensure directory exists
    os.makedirs(os.path.dirname(json_file), exist_ok=True)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(hscodes)} HS codes to {json_file}")


def convert_sections_csv_to_json(csv_file: str, json_file: str):
    """Convert sections CSV to JSON format."""
    sections = []

    try:
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # Handle potential BOM in column names
                section_key = "section"
                if section_key not in row:
                    # Look for section key with BOM
                    section_key = next(
                        (k for k in row.keys() if k.endswith("section")), "section"
                    )

                section_entry = {"section": row[section_key], "name": row["name"]}
                sections.append(section_entry)
    except Exception as e:
        print(f"Error processing sections CSV: {e}")
        print(
            f"Available keys: {list(row.keys()) if 'row' in locals() else 'No row data'}"
        )
        raise

    # Create the JSON structure expected by the database
    json_data = {"sections": sections}

    # Ensure directory exists
    os.makedirs(os.path.dirname(json_file), exist_ok=True)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(sections)} sections to {json_file}")


def main():
    """Main conversion function."""
    # Define paths
    base_dir = Path(__file__).parent
    databases_dir = base_dir / "src" / "pyhscodes" / "databases"

    # Input CSV files (expected to be in the project root)
    hscodes_csv = base_dir / "harmonized-system.csv"
    sections_csv = base_dir / "sections.csv"

    # Output JSON files
    hscodes_json = databases_dir / "hscodes.json"
    sections_json = databases_dir / "sections.json"

    # Check if input files exist
    if not hscodes_csv.exists():
        print(f"Error: {hscodes_csv} not found.")
        print(
            "Please place your HS codes CSV file in the project root as 'harmonized-system.csv'"
        )
        print("Expected columns: section,hscode,description,parent,level")
        return 1

    if not sections_csv.exists():
        print(f"Error: {sections_csv} not found.")
        print(
            "Please place your sections CSV file in the project root as 'sections.csv'"
        )
        print("Expected columns: section,name")
        return 1

    try:
        # Convert both files
        convert_hscodes_csv_to_json(str(hscodes_csv), str(hscodes_json))
        convert_sections_csv_to_json(str(sections_csv), str(sections_json))

        print("\nConversion completed successfully!")
        print(f"JSON files created in: {databases_dir}")

    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
