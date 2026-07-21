import pytest

from torah_codes.corpus.parser import parse_verse_line
from torah_codes.exceptions import VerseParseError


def test_parse_verse_line() -> None:
    verse = parse_verse_line(
        "GEN 001:001 BRASYT BRA ALHYm AT HSMYm VAT HARc.\n",
        expected_book_code="GEN",
        book_index=0,
        source_line_number=1,
    )

    assert str(verse.reference) == "GEN 001:001"
    assert verse.raw_text == "BRASYT BRA ALHYm AT HSMYm VAT HARc."


def test_rejects_wrong_book_code() -> None:
    with pytest.raises(VerseParseError):
        parse_verse_line(
            "EXO 001:001 BRASYT.",
            expected_book_code="GEN",
            book_index=0,
            source_line_number=1,
        )
