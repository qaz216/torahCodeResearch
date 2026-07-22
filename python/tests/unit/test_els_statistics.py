"""Tests for descriptive ELS statistics."""

import pytest

from torah_codes.els import ELSMatch
from torah_codes.els_statistics import summarize_els_matches


def _match(skip: int, start: int) -> ELSMatch:
    return ELSMatch(
        word="TVRH",
        skip=skip,
        indices=(start, start + skip, start + (2 * skip), start + (3 * skip)),
        positions=(),
    )


def test_summarizes_match_distribution() -> None:
    statistics = summarize_els_matches(
        "TVRH",
        -2,
        2,
        (
            _match(-2, 10),
            _match(1, 20),
            _match(1, 30),
            _match(2, 40),
        ),
    )

    assert statistics.total_matches == 4
    assert statistics.matched_skip_count == 3
    assert tuple(
        (frequency.skip, frequency.matches)
        for frequency in statistics.frequencies
    ) == ((-2, 1), (-1, 0), (1, 2), (2, 1))
    assert statistics.best_match == _match(1, 20)
    assert statistics.mean_absolute_skip == pytest.approx(1.5)
    assert statistics.median_absolute_skip == pytest.approx(1.5)
    assert tuple(
        (frequency.skip, frequency.matches)
        for frequency in statistics.peak_frequencies
    ) == ((1, 2),)


def test_empty_statistics_use_none_for_undefined_values() -> None:
    statistics = summarize_els_matches("TVRH", -2, 2, ())

    assert statistics.total_matches == 0
    assert statistics.matched_skip_count == 0
    assert statistics.best_match is None
    assert statistics.mean_absolute_skip is None
    assert statistics.median_absolute_skip is None
    assert statistics.peak_frequencies == ()


def test_best_match_tie_breaking_is_deterministic() -> None:
    negative = _match(-2, 50)
    positive = _match(2, 10)

    statistics = summarize_els_matches(
        "TVRH",
        -2,
        2,
        (positive, negative),
    )

    assert statistics.best_match == negative


def test_rejects_zero_only_range() -> None:
    with pytest.raises(
        ValueError,
        match="at least one nonzero skip",
    ):
        summarize_els_matches("TVRH", 0, 0, ())
