"""Tests for verse lookup and Hebrew rendering."""

import pytest

from torah_codes.corpus.models import Verse, VerseReference
from torah_codes.verse_output import format_verse, parse_verse_reference


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2:23:1", VerseReference(1, 23, 1, "EXO")),
        ("EXO 23:1", VerseReference(1, 23, 1, "EXO")),
        ("exo:23:1", VerseReference(1, 23, 1, "EXO")),
    ],
)
def test_parses_supported_references(value: str, expected: VerseReference) -> None:
    assert parse_verse_reference(value) == expected


@pytest.mark.parametrize("value", ["6:1:1", "EXO 0:1", "Exodus 23:1", "2:23"])
def test_rejects_invalid_references(value: str) -> None:
    with pytest.raises(ValueError):
        parse_verse_reference(value)


def test_formats_readable_hebrew_and_preserves_punctuation() -> None:
    verse = Verse(VerseReference(1, 23, 1, "EXO"), "LA TsA SMO.", 1)
    assert format_verse(verse, output_format="hebrew", letters_only=False) == "לא תשא שמע."


def test_formats_letters_only_hebrew() -> None:
    verse = Verse(VerseReference(1, 23, 1, "EXO"), "LA-TsA.", 1)
    assert format_verse(verse, output_format="hebrew", letters_only=True) == "לאתשא"


def test_formats_original_transliteration() -> None:
    verse = Verse(VerseReference(1, 23, 1, "EXO"), "LA-TsA.", 1)
    assert format_verse(verse, output_format="transliteration", letters_only=False) == "LA-TsA."
