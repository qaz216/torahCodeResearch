"""Proximity analysis for pairs of Equidistant Letter Sequence matches."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import product

from torah_codes.corpus.models import TorahCorpus
from torah_codes.els import ELSMatch, find_els_range


@dataclass(frozen=True, slots=True)
class ELSPair:
    """Spatial relationship between two ELS occurrences."""

    left: ELSMatch
    right: ELSMatch
    start_distance: int
    minimum_letter_distance: int
    combined_span: int
    intersects: bool
    spans_overlap: bool


def _bounds(match: ELSMatch) -> tuple[int, int]:
    return min(match.indices), max(match.indices)


def compare_match_pair(left: ELSMatch, right: ELSMatch) -> ELSPair:
    """Calculate deterministic proximity measurements for two matches."""

    if not left.indices or not right.indices:
        raise ValueError("ELS matches must contain at least one index")

    left_start, left_end = _bounds(left)
    right_start, right_end = _bounds(right)
    left_indices = set(left.indices)
    right_indices = set(right.indices)

    return ELSPair(
        left=left,
        right=right,
        start_distance=abs(left.start_index - right.start_index),
        minimum_letter_distance=min(
            abs(left_index - right_index)
            for left_index in left.indices
            for right_index in right.indices
        ),
        combined_span=max(left_end, right_end) - min(left_start, right_start),
        intersects=bool(left_indices & right_indices),
        spans_overlap=max(left_start, right_start) <= min(left_end, right_end),
    )


def _pair_sort_key(pair: ELSPair) -> tuple[int, int, int, int, int, int, int, int]:
    return (
        pair.minimum_letter_distance,
        pair.combined_span,
        abs(pair.left.skip),
        abs(pair.right.skip),
        pair.left.skip,
        pair.right.skip,
        pair.left.start_index,
        pair.right.start_index,
    )


def pair_els_matches(
    left_matches: tuple[ELSMatch, ...],
    right_matches: tuple[ELSMatch, ...],
    *,
    max_distance: int | None = None,
    same_word: bool = False,
) -> tuple[ELSPair, ...]:
    """Pair two match collections and return them in proximity order.

    For a word compared with itself, self-pairs and mirrored duplicates are
    excluded by pairing each distinct occurrence only once.
    """

    if max_distance is not None and max_distance < 0:
        raise ValueError("max_distance must be zero or greater")

    candidates: Iterable[tuple[ELSMatch, ELSMatch]]

    if same_word:
        candidates = (
            (left_matches[left_index], left_matches[right_index])
            for left_index in range(len(left_matches))
            for right_index in range(left_index + 1, len(left_matches))
        )
    else:
        candidates = product(left_matches, right_matches)

    pairs = []
    for left, right in candidates:
        pair = compare_match_pair(left, right)
        if max_distance is None or pair.minimum_letter_distance <= max_distance:
            pairs.append(pair)

    return tuple(sorted(pairs, key=_pair_sort_key))


def find_els_pairs(
    corpus: TorahCorpus,
    left_word: str,
    right_word: str,
    min_skip: int,
    max_skip: int,
    *,
    book_code: str | None = None,
    max_distance: int | None = None,
) -> tuple[ELSPair, ...]:
    """Search two words and return all qualifying occurrence pairs."""

    normalized_left = left_word.strip()
    normalized_right = right_word.strip()
    if not normalized_left or not normalized_right:
        raise ValueError("words must not be empty")

    left_matches = find_els_range(
        corpus,
        normalized_left,
        min_skip,
        max_skip,
        book_code=book_code,
    )
    right_matches = (
        left_matches
        if normalized_left == normalized_right
        else find_els_range(
            corpus,
            normalized_right,
            min_skip,
            max_skip,
            book_code=book_code,
        )
    )

    return pair_els_matches(
        left_matches,
        right_matches,
        max_distance=max_distance,
        same_word=normalized_left == normalized_right,
    )
