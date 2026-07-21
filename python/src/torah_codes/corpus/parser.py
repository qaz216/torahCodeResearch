"""Strict parser for one-verse-per-line Torah source files."""

from __future__ import annotations

import re

from torah_codes.corpus.models import Verse, VerseReference
from torah_codes.exceptions import VerseParseError

VERSE_PATTERN = re.compile(
    r"^(?P<book>[A-Z]{3}) (?P<chapter>\d{3}):(?P<verse>\d{3}) (?P<text>.+)$"
)


def parse_verse_line(
    raw_line: str,
    *,
    expected_book_code: str,
    book_index: int,
    source_line_number: int,
) -> Verse:
    line = raw_line.rstrip("\r\n")
    match = VERSE_PATTERN.fullmatch(line)
    if match is None:
        raise VerseParseError(
            f"Malformed verse line {source_line_number}: {line!r}"
        )

    book_code = match.group("book")
    if book_code != expected_book_code:
        raise VerseParseError(
            f"Line {source_line_number} has book code {book_code!r}; "
            f"expected {expected_book_code!r}"
        )

    chapter = int(match.group("chapter"))
    verse_number = int(match.group("verse"))
    if chapter < 1 or verse_number < 1:
        raise VerseParseError(
            f"Line {source_line_number} contains a zero chapter or verse number"
        )

    return Verse(
        reference=VerseReference(book_index, chapter, verse_number, book_code),
        raw_text=match.group("text"),
        source_line_number=source_line_number,
    )
