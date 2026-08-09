"""Verse reference parsing and display formatting."""

from __future__ import annotations

import re

from torah_codes.corpus.books import BOOKS, BOOK_BY_CODE, BOOK_INDEX_BY_CODE
from torah_codes.corpus.models import TorahCorpus, Verse, VerseReference


HEBREW_BY_TRANSLITERATION = {
    "A": "א",
    "B": "ב",
    "G": "ג",
    "D": "ד",
    "H": "ה",
    "V": "ו",
    "Z": "ז",
    "X": "ח",
    "+": "ט",
    "Y": "י",
    "K": "כ",
    "k": "ך",
    "L": "ל",
    "M": "מ",
    "m": "ם",
    "N": "נ",
    "n": "ן",
    "$": "ס",
    "O": "ע",
    "P": "פ",
    "p": "ף",
    "C": "צ",
    "c": "ץ",
    "Q": "ק",
    "R": "ר",
    "S": "ש",
    "s": "ש",
    "#": "ש",
    "T": "ת",
}

_NUMERIC_REFERENCE = re.compile(r"^(?P<book>[1-5]):(?P<chapter>\d+):(?P<verse>\d+)$")
_CODE_REFERENCE = re.compile(
    r"^(?P<book>GEN|EXO|LEV|NUM|DEU)(?:\s+|:)(?P<chapter>\d+):(?P<verse>\d+)$",
    re.IGNORECASE,
)
_GLOBAL_VERSE_NUMBER = re.compile(r"^[+-]?\d+$")


def is_global_verse_number(value: str) -> bool:
    """Return whether a value has the syntax of a global verse number."""

    return _GLOBAL_VERSE_NUMBER.fullmatch(value.strip()) is not None


def find_verse_by_number(corpus: TorahCorpus, number: int) -> Verse:
    """Return a verse by its one-based position in canonical Torah order."""

    verse_count = len(corpus.verses)
    if number < 1 or number > verse_count:
        raise ValueError(f"global verse number must be between 1 and {verse_count}; got {number}")
    return corpus.verses[number - 1]


def parse_verse_reference(value: str) -> VerseReference:
    """Parse ``2:23:1``, ``EXO 23:1``, or ``EXO:23:1``."""

    normalized = " ".join(value.strip().split())
    match = _NUMERIC_REFERENCE.fullmatch(normalized)
    if match is not None:
        book_index = int(match.group("book")) - 1
        book_code = BOOKS[book_index].code
    else:
        match = _CODE_REFERENCE.fullmatch(normalized)
        if match is None:
            raise ValueError(
                "invalid verse reference; use a global verse number (5423), "
                "BOOK:CHAPTER:VERSE (2:23:1), or CODE CHAPTER:VERSE (EXO 23:1)"
            )
        book_code = match.group("book").upper()
        book_index = BOOK_INDEX_BY_CODE[book_code]

    chapter = int(match.group("chapter"))
    verse = int(match.group("verse"))
    if chapter < 1 or verse < 1:
        raise ValueError("chapter and verse numbers must be greater than zero")
    return VerseReference(book_index, chapter, verse, book_code)


def find_verse(corpus: TorahCorpus, reference: VerseReference) -> Verse:
    """Return a verse or raise a user-facing error when it does not exist."""

    for verse in corpus.verses:
        if verse.reference == reference:
            return verse
    book_name = BOOK_BY_CODE[reference.book_code].name
    raise ValueError(f"verse not found: {book_name} {reference.chapter}:{reference.verse}")


def format_verse(verse: Verse, *, output_format: str, letters_only: bool) -> str:
    """Format a source verse as Hebrew or canonical transliteration."""

    text = verse.raw_text
    if letters_only:
        text = "".join(character for character in text if character in HEBREW_BY_TRANSLITERATION)

    if output_format == "transliteration":
        return text
    if output_format == "hebrew":
        return "".join(HEBREW_BY_TRANSLITERATION.get(character, character) for character in text)
    raise ValueError(f"unsupported verse output format: {output_format}")
