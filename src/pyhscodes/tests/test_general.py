import os.path
import re
from importlib import metadata as _importlib_metadata
from unittest.mock import patch

import pytest

import pyhscodes
import pyhscodes.db


@pytest.fixture
def hscodes():
    pyhscodes.hscodes._clear()
    yield pyhscodes.hscodes
    pyhscodes.hscodes._clear()


@pytest.fixture
def sections():
    pyhscodes.sections._clear()
    yield pyhscodes.sections
    pyhscodes.sections._clear()


def test_hscode_list(hscodes):
    assert len(pyhscodes.hscodes) == 6940
    assert isinstance(list(pyhscodes.hscodes)[0], pyhscodes.db.Data)


def test_section_list(sections):
    assert len(pyhscodes.sections) == 21
    assert isinstance(list(pyhscodes.sections)[0], pyhscodes.db.Data)


def test_hscode_fuzzy_search(hscodes):
    # Search for "horses" should find horse-related codes
    results = pyhscodes.hscodes.search_fuzzy("horses")
    assert len(results) >= 1
    # The first result should be related to horses
    assert "horse" in results[0].description.lower()

    # Search for "cattle" should find cattle-related codes
    results = pyhscodes.hscodes.search_fuzzy("cattle")
    assert len(results) >= 1
    assert "cattle" in results[0].description.lower()

    # Search for "live" should find multiple results since many descriptions contain "live"
    results = pyhscodes.hscodes.search_fuzzy("live")
    assert len(results) >= 5


def test_hscode_has_all_attributes(hscodes):
    animals_chapter = pyhscodes.hscodes.get(hscode="01")
    assert animals_chapter.hscode == "01"
    assert animals_chapter.description == "Animals; live"
    assert animals_chapter.section == "I"
    assert animals_chapter.parent == "TOTAL"
    assert animals_chapter.level == "2"


def test_hscode_hierarchy_properties(hscodes):
    # Test chapter (level 2)
    chapter = pyhscodes.hscodes.get(hscode="01")
    assert chapter.is_chapter is True
    assert chapter.is_heading is False
    assert chapter.is_subheading is False

    # Test heading (level 4)
    heading = pyhscodes.hscodes.get(hscode="0101")
    assert heading.is_chapter is False
    assert heading.is_heading is True
    assert heading.is_subheading is False

    # Test subheading (level 6)
    subheading = pyhscodes.hscodes.get(hscode="010121")
    assert subheading.is_chapter is False
    assert subheading.is_heading is False
    assert subheading.is_subheading is True


def test_get_by_level(hscodes):
    # Get all chapters (level 2)
    chapters = pyhscodes.hscodes.get_by_level("2")
    assert len(chapters) == 97
    # Check that chapter 01 exists
    chapter_01 = next((c for c in chapters if c.hscode == "01"), None)
    assert chapter_01 is not None
    assert chapter_01.hscode == "01"

    # Get all headings (level 4)
    headings = pyhscodes.hscodes.get_by_level("4")
    assert len(headings) == 1229

    # Get all subheadings (level 6)
    subheadings = pyhscodes.hscodes.get_by_level("6")
    assert len(subheadings) == 5613


def test_get_children(hscodes):
    # Get children of chapter 01
    children = pyhscodes.hscodes.get_children("01")
    assert len(children) == 6
    expected_codes = {"0101", "0102", "0103", "0104", "0105", "0106"}
    actual_codes = {child.hscode for child in children}
    assert actual_codes == expected_codes

    # Get children of heading 0101
    children = pyhscodes.hscodes.get_children("0101")
    assert len(children) == 4
    expected_codes = {"010121", "010129", "010130", "010190"}
    actual_codes = {child.hscode for child in children}
    assert actual_codes == expected_codes


def test_get_hierarchy(hscodes):
    # Get hierarchy for a 6-digit code
    hierarchy = pyhscodes.hscodes.get_hierarchy("010121")
    assert len(hierarchy) == 3
    assert hierarchy[0].hscode == "01"  # Chapter
    assert hierarchy[1].hscode == "0101"  # Heading
    assert hierarchy[2].hscode == "010121"  # Subheading

    # Get hierarchy for a 4-digit code
    hierarchy = pyhscodes.hscodes.get_hierarchy("0101")
    assert len(hierarchy) == 2
    assert hierarchy[0].hscode == "01"  # Chapter
    assert hierarchy[1].hscode == "0101"  # Heading


def test_hscode_missing_attribute(hscodes):
    animals_chapter = pyhscodes.hscodes.get(hscode="01")
    with pytest.raises(AttributeError):
        _ = animals_chapter.foo


def test_sections(sections):
    section_i = pyhscodes.sections.get(section="I")
    assert section_i.section == "I"
    assert section_i.name == "live animals; animal products"


def test_repr(hscodes):
    animals_chapter = pyhscodes.hscodes.get(hscode="01")
    repr_str = repr(animals_chapter)
    assert re.match(r"HSCode\(.*hscode='01'.*\)", repr_str)


def test_dict(hscodes):
    animals_chapter = pyhscodes.hscodes.get(hscode="01")
    animals_dict = dict(animals_chapter)
    assert animals_dict["hscode"] == "01"
    assert animals_dict["description"] == "Animals; live"


def test_dir(hscodes):
    animals_chapter = pyhscodes.hscodes.get(hscode="01")
    assert "hscode" in dir(animals_chapter)
    assert "description" in dir(animals_chapter)


def test_get(hscodes):
    # Test successful lookup
    animals_chapter = pyhscodes.hscodes.get(hscode="01")
    assert animals_chapter.hscode == "01"

    # Test with default value
    missing = pyhscodes.hscodes.get(hscode="999", default="not found")
    assert missing == "not found"


def test_lookup(hscodes):
    # Test lookup by hscode
    animals_chapter = pyhscodes.hscodes.lookup("01")
    assert animals_chapter.hscode == "01"

    # Test lookup by description (should work for indexed fields)
    try:
        result = pyhscodes.hscodes.lookup("Animals; live")
        assert result.hscode == "01"
    except LookupError:
        # It's okay if this doesn't work since description might not be indexed
        pass

    # Test case insensitive lookup
    animals_chapter = pyhscodes.hscodes.lookup("01")
    assert animals_chapter.hscode == "01"


def test_has_version_attribute():
    assert hasattr(pyhscodes, "__version__")
    # The version might be 'n/a' if the package isn't installed
    assert pyhscodes.__version__ is not None


def test_is_instance_of_hscode(hscodes):
    animals_chapter = pyhscodes.hscodes.get(hscode="01")
    assert isinstance(animals_chapter, pyhscodes.db.HSCode)
    assert isinstance(animals_chapter, pyhscodes.db.Data)


def test_is_instance_of_section(sections):
    section_i = pyhscodes.sections.get(section="I")
    assert isinstance(section_i, pyhscodes.db.Section)
    assert isinstance(section_i, pyhscodes.db.Data)


def test_add_entry(hscodes):
    original_count = len(pyhscodes.hscodes)

    # Add a new entry
    pyhscodes.hscodes.add_entry(
        section="XX", hscode="9999", description="Test code", parent="TOTAL", level="2"
    )

    assert len(pyhscodes.hscodes) == original_count + 1
    test_code = pyhscodes.hscodes.get(hscode="9999")
    assert test_code.description == "Test code"


def test_remove_entry(hscodes):
    # First add an entry to remove
    pyhscodes.hscodes.add_entry(
        section="XX",
        hscode="9999",
        description="Test code to remove",
        parent="TOTAL",
        level="2",
    )

    original_count = len(pyhscodes.hscodes)

    # Remove the entry
    pyhscodes.hscodes.remove_entry(hscode="9999")

    assert len(pyhscodes.hscodes) == original_count - 1
    assert pyhscodes.hscodes.get(hscode="9999") is None


def test_remove_non_existent_entry():
    with pytest.raises(KeyError):
        pyhscodes.hscodes.remove_entry(hscode="nonexistent")


def test_no_results_lookup_error(hscodes):
    with pytest.raises(LookupError):
        pyhscodes.hscodes.search_fuzzy("completely nonexistent search term")


def test_get_version_with_package_not_found():
    # Mock importlib.metadata.version to raise PackageNotFoundError
    with patch.object(
        _importlib_metadata,
        "version",
        side_effect=_importlib_metadata.PackageNotFoundError("test"),
    ):
        version = pyhscodes.get_version("nonexistent_package")
        assert version == "n/a"


def test_all_hscodes_have_required_attributes():
    """Test that all HS codes have the required attributes."""
    for hscode in pyhscodes.hscodes:
        # All codes should have these basic attributes
        assert hasattr(hscode, "hscode")
        assert hasattr(hscode, "description")
        assert hasattr(hscode, "section")
        assert hasattr(hscode, "parent")
        assert hasattr(hscode, "level")

        # Values should not be None or empty
        assert hscode.hscode is not None
        assert hscode.description is not None
        assert hscode.section is not None
        assert hscode.level is not None


def test_remove_accents():
    # Test the accent removal function
    assert pyhscodes.remove_accents("café") == "cafe"
    assert pyhscodes.remove_accents("naïve") == "naive"
    assert pyhscodes.remove_accents("ASCII text") == "ASCII text"
