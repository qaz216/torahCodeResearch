"""Descriptive statistics for Equidistant Letter Sequence searches."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from statistics import fmean, median

from torah_codes.corpus.models import TorahCorpus
from torah_codes.els import ELSMatch, find_els_range


@dataclass(frozen=True, slots=True)
class SkipFrequency:
    """Number of ELS occurrences found at one signed skip."""

    skip: int
    matches: int


@dataclass(frozen=True, slots=True)
class ELSStatistics:
    """Descriptive results for one word over a signed skip range."""

    word: str
    min_skip: int
    max_skip: int
    total_matches: int
    frequencies: tuple[SkipFrequency, ...]
    best_match: ELSMatch | None
    mean_absolute_skip: float | None
    median_absolute_skip: float | None

    @property
    def matched_skip_count(self) -> int:
        """Return the number of signed skips having at least one occurrence."""
        return sum(frequency.matches > 0 for frequency in self.frequencies)

    @property
    def peak_frequencies(self) -> tuple[SkipFrequency, ...]:
        """Return all signed skips tied for the largest match count."""
        if not self.frequencies:
            return ()

        peak = max(frequency.matches for frequency in self.frequencies)
        if peak == 0:
            return ()

        return tuple(
            frequency
            for frequency in self.frequencies
            if frequency.matches == peak
        )


def summarize_els_matches(
    word: str,
    min_skip: int,
    max_skip: int,
    matches: tuple[ELSMatch, ...],
) -> ELSStatistics:
    """Build descriptive statistics from an already-computed match collection."""

    if min_skip > max_skip:
        raise ValueError("min_skip must be less than or equal to max_skip")
    if min_skip == 0 and max_skip == 0:
        raise ValueError("skip range must include at least one nonzero skip")

    counts = Counter(match.skip for match in matches)
    frequencies = tuple(
        SkipFrequency(skip=skip, matches=counts[skip])
        for skip in range(min_skip, max_skip + 1)
        if skip != 0
    )

    ordered_matches = tuple(
        sorted(
            matches,
            key=lambda match: (
                abs(match.skip),
                match.skip,
                match.start_index,
            ),
        )
    )
    absolute_skips = [abs(match.skip) for match in matches]

    return ELSStatistics(
        word=word,
        min_skip=min_skip,
        max_skip=max_skip,
        total_matches=len(matches),
        frequencies=frequencies,
        best_match=ordered_matches[0] if ordered_matches else None,
        mean_absolute_skip=fmean(absolute_skips) if absolute_skips else None,
        median_absolute_skip=float(median(absolute_skips))
        if absolute_skips
        else None,
    )


def calculate_els_statistics(
    corpus: TorahCorpus,
    word: str,
    min_skip: int,
    max_skip: int,
    *,
    book_code: str | None = None,
) -> ELSStatistics:
    """Search a corpus and calculate descriptive ELS statistics."""

    matches = find_els_range(
        corpus,
        word,
        min_skip,
        max_skip,
        book_code=book_code,
    )
    return summarize_els_matches(word, min_skip, max_skip, matches)
