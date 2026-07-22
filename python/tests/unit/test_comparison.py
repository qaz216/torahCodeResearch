"""Tests for ELS word comparisons."""

import pytest

from torah_codes.comparison import compare_els_statistics
from torah_codes.els import ELSMatch
from torah_codes.els_statistics import summarize_els_matches


def _match(word: str, skip: int, start: int) -> ELSMatch:
    return ELSMatch(
        word=word,
        skip=skip,
        indices=(start, start + skip),
        positions=(),
    )


def test_compares_two_statistics_objects() -> None:
    left = summarize_els_matches(
        "TVRH",
        -2,
        2,
        (
            _match("TVRH", -2, 10),
            _match("TVRH", 1, 20),
            _match("TVRH", 1, 30),
        ),
    )
    right = summarize_els_matches(
        "ALHYM",
        -2,
        2,
        (
            _match("ALHYM", -2, 40),
            _match("ALHYM", 2, 50),
        ),
    )

    comparison = compare_els_statistics(left, right)

    assert comparison.match_count_ratio == pytest.approx(1.5)
    assert comparison.shared_matched_skips == (-2,)
    assert comparison.best_absolute_skip_difference == 1


def test_zero_right_matches_has_no_ratio() -> None:
    left = summarize_els_matches(
        "TVRH",
        -1,
        1,
        (_match("TVRH", 1, 10),),
    )
    right = summarize_els_matches("ALHYM", -1, 1, ())

    comparison = compare_els_statistics(left, right)

    assert comparison.match_count_ratio is None
    assert comparison.best_absolute_skip_difference is None


def test_rejects_different_skip_ranges() -> None:
    left = summarize_els_matches("TVRH", -2, 2, ())
    right = summarize_els_matches("ALHYM", -3, 3, ())

    with pytest.raises(ValueError, match="same skip range"):
        compare_els_statistics(left, right)
