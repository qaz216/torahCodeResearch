"""Proximity analysis for pairs of Equidistant Letter Sequence matches."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import product
from typing import Literal

from torah_codes.corpus.models import TorahCorpus
from torah_codes.els import ELSMatch, find_els_range

PairRelationship = Literal["shared-letter", "crossing", "disjoint"]


@dataclass(frozen=True, slots=True)
class ELSPair:
    """Spatial relationship between two ELS occurrences."""

    left: ELSMatch
    right: ELSMatch
    start_distance: int
    minimum_letter_distance: int
    combined_span: int
    shared_letter_count: int
    relationship: PairRelationship

    @property
    def intersects(self) -> bool:
        """Return whether the two occurrences select any identical positions."""

        return self.shared_letter_count > 0

    @property
    def spans_overlap(self) -> bool:
        """Return whether the bounding spans overlap."""

        return self.relationship != "disjoint"


@dataclass(frozen=True, slots=True)
class ProximityFilters:
    """Optional filters applied while pairing ELS occurrences."""

    max_distance: int | None = None
    max_span: int | None = None
    exclude_shared_letters: bool = False
    exclude_crossing: bool = False
    literal_left: bool = False
    literal_right: bool = False

    def __post_init__(self) -> None:
        if self.max_distance is not None and self.max_distance < 0:
            raise ValueError("max_distance must be zero or greater")
        if self.max_span is not None and self.max_span < 0:
            raise ValueError("max_span must be zero or greater")


def _bounds(match: ELSMatch) -> tuple[int, int]:
    return min(match.indices), max(match.indices)


def compare_match_pair(left: ELSMatch, right: ELSMatch) -> ELSPair:
    """Calculate deterministic proximity measurements for two matches."""

    if not left.indices or not right.indices:
        raise ValueError("ELS matches must contain at least one index")

    left_start, left_end = _bounds(left)
    right_start, right_end = _bounds(right)
    shared_letter_count = len(set(left.indices) & set(right.indices))
    spans_overlap = max(left_start, right_start) <= min(left_end, right_end)

    relationship: PairRelationship
    if shared_letter_count:
        relationship = "shared-letter"
    elif spans_overlap:
        relationship = "crossing"
    else:
        relationship = "disjoint"

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
        shared_letter_count=shared_letter_count,
        relationship=relationship,
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


def _passes_filters(pair: ELSPair, filters: ProximityFilters) -> bool:
    if (
        filters.max_distance is not None
        and pair.minimum_letter_distance > filters.max_distance
    ):
        return False
    if filters.max_span is not None and pair.combined_span > filters.max_span:
        return False
    if filters.exclude_shared_letters and pair.relationship == "shared-letter":
        return False
    if filters.exclude_crossing and pair.relationship == "crossing":
        return False
    if filters.literal_left and pair.left.skip != 1:
        return False
    if filters.literal_right and pair.right.skip != 1:
        return False
    return True


def pair_els_matches(
    left_matches: tuple[ELSMatch, ...],
    right_matches: tuple[ELSMatch, ...],
    *,
    max_distance: int | None = None,
    max_span: int | None = None,
    exclude_shared_letters: bool = False,
    exclude_crossing: bool = False,
    literal_left: bool = False,
    literal_right: bool = False,
    same_word: bool = False,
) -> tuple[ELSPair, ...]:
    """Pair two match collections and return them in proximity order.

    ``shared-letter`` pairs select at least one identical corpus position.
    ``crossing`` pairs have overlapping bounding spans but no selected position
    in common. ``disjoint`` pairs have separate bounding spans.

    For a word compared with itself, self-pairs and mirrored duplicates are
    excluded by pairing each distinct occurrence only once.
    """

    filters = ProximityFilters(
        max_distance=max_distance,
        max_span=max_span,
        exclude_shared_letters=exclude_shared_letters,
        exclude_crossing=exclude_crossing,
        literal_left=literal_left,
        literal_right=literal_right,
    )

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
        if _passes_filters(pair, filters):
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
    max_span: int | None = None,
    exclude_shared_letters: bool = False,
    exclude_crossing: bool = False,
    literal_left: bool = False,
    literal_right: bool = False,
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
        max_span=max_span,
        exclude_shared_letters=exclude_shared_letters,
        exclude_crossing=exclude_crossing,
        literal_left=literal_left,
        literal_right=literal_right,
        same_word=normalized_left == normalized_right,
    )
