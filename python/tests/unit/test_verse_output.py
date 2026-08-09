"""Tests for verse lookup and Hebrew rendering."""

import pytest

from torah_codes.corpus.models import TorahCorpus, Verse, VerseReference
from torah_codes.verse_output import (
    find_verse_by_number,
    format_verse,
    is_global_verse_number,
    parse_verse_reference,
)


def _corpus_with_three_verses() -> TorahCorpus:
    verses = [
        Verse(VerseReference(0, 1, number, "GEN"), f"VERSE-{number}", number)
        for number in range(1, 4)
    ]
    return TorahCorpus.create(
        verses=verses,
        text="",
        positions=[],
        book_ranges={},
        verse_ranges={},
    )


@pytest.mark.parametrize("value", ["1", "5423", "+5852"])
def test_recognizes_global_verse_numbers(value: str) -> None:
    assert is_global_verse_number(value)


@pytest.mark.parametrize("value", ["2:23:1", "EXO 23:1", "1.5", "verse"])
def test_does_not_misidentify_references_as_global_numbers(value: str) -> None:
    assert not is_global_verse_number(value)


def test_finds_verse_by_one_based_global_number() -> None:
    corpus = _corpus_with_three_verses()
    assert find_verse_by_number(corpus, 1).raw_text == "VERSE-1"
    assert find_verse_by_number(corpus, 3).raw_text == "VERSE-3"


@pytest.mark.parametrize("number", [0, -1, 4])
def test_rejects_global_verse_number_outside_corpus(number: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 3"):
        find_verse_by_number(_corpus_with_three_verses(), number)


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
