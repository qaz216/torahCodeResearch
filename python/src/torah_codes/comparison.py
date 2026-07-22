"""Comparison utilities for Equidistant Letter Sequence analyses."""

from __future__ import annotations

from dataclasses import dataclass

from torah_codes.corpus.models import TorahCorpus
from torah_codes.els_statistics import ELSStatistics, calculate_els_statistics


@dataclass(frozen=True, slots=True)
class ELSComparison:
    """Descriptive comparison of two words over the same search range."""

    left: ELSStatistics
    right: ELSStatistics
    shared_matched_skips: tuple[int, ...]

    @property
    def match_count_ratio(self) -> float | None:
        """Return left matches divided by right matches."""
        if self.right.total_matches == 0:
            return None
        return self.left.total_matches / self.right.total_matches

    @property
    def best_absolute_skip_difference(self) -> int | None:
        """Return the difference between the best absolute skips."""
        if self.left.best_match is None or self.right.best_match is None:
            return None
        return abs(abs(self.left.best_match.skip) - abs(self.right.best_match.skip))


def compare_els_statistics(
    left: ELSStatistics,
    right: ELSStatistics,
) -> ELSComparison:
    """Compare two compatible ELS statistics objects."""

    if (left.min_skip, left.max_skip) != (right.min_skip, right.max_skip):
        raise ValueError("statistics must use the same skip range")

    left_skips = {
        frequency.skip
        for frequency in left.frequencies
        if frequency.matches > 0
    }
    right_skips = {
        frequency.skip
        for frequency in right.frequencies
        if frequency.matches > 0
    }

    return ELSComparison(
        left=left,
        right=right,
        shared_matched_skips=tuple(sorted(left_skips & right_skips)),
    )


def compare_els_words(
    corpus: TorahCorpus,
    left_word: str,
    right_word: str,
    min_skip: int,
    max_skip: int,
    *,
    book_code: str | None = None,
) -> ELSComparison:
    """Search and compare two words over the same scope and skip range."""

    left = calculate_els_statistics(
        corpus,
        left_word,
        min_skip,
        max_skip,
        book_code=book_code,
    )
    right = calculate_els_statistics(
        corpus,
        right_word,
        min_skip,
        max_skip,
        book_code=book_code,
    )
    return compare_els_statistics(left, right)
