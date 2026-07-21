"""Reproducibility checks for the commonly cited Weismandel pattern."""

from pathlib import Path

from torah_codes.corpus.loader import load_torah
from torah_codes.els import ELSMatch, find_els


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def book_relative_indices(
    corpus_start: int,
    match: ELSMatch,
) -> tuple[int, ...]:
    """Return zero-based indices relative to the beginning of a book."""
    return tuple(index - corpus_start for index in match.indices)


def assert_expected_match(
    *,
    word: str,
    skip: int,
    book_code: str,
    expected_indices: tuple[int, ...],
) -> None:
    corpus = load_torah(PROJECT_ROOT)
    book_range = corpus.range_for_book(book_code)

    matches = find_els(
        corpus,
        word,
        skip,
        book_code=book_code,
    )

    actual_matches = {
        book_relative_indices(book_range.start, match)
        for match in matches
    }

    assert expected_indices in actual_matches


def test_genesis_torah_at_plus_fifty() -> None:
    assert_expected_match(
        word="TVRH",
        skip=50,
        book_code="GEN",
        expected_indices=(5, 55, 105, 155),
    )


def test_exodus_torah_at_plus_fifty() -> None:
    assert_expected_match(
        word="TVRH",
        skip=50,
        book_code="EXO",
        expected_indices=(7, 57, 107, 157),
    )


def test_leviticus_divine_name_at_plus_seven() -> None:
    assert_expected_match(
        word="YHVH",
        skip=7,
        book_code="LEV",
        expected_indices=(22199, 22206, 22213, 22220),
    )


def test_numbers_torah_at_minus_fifty() -> None:
    assert_expected_match(
        word="TVRH",
        skip=-50,
        book_code="NUM",
        expected_indices=(163, 113, 63, 13),
    )


def test_deuteronomy_torah_at_minus_forty_nine() -> None:
    assert_expected_match(
        word="TVRH",
        skip=-49,
        book_code="DEU",
        expected_indices=(425, 376, 327, 278),
    )
