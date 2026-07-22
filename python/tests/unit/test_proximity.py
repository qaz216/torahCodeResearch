"""Tests for ELS proximity analysis."""

import pytest

from torah_codes.els import ELSMatch
from torah_codes.proximity import compare_match_pair, pair_els_matches


def _match(word: str, skip: int, indices: tuple[int, ...]) -> ELSMatch:
    return ELSMatch(word=word, skip=skip, indices=indices, positions=())


def test_shared_letter_sequences_are_classified_explicitly() -> None:
    pair = compare_match_pair(
        _match("ABC", 5, (10, 15, 20)),
        _match("XYZ", -3, (23, 20, 17)),
    )

    assert pair.minimum_letter_distance == 0
    assert pair.shared_letter_count == 1
    assert pair.relationship == "shared-letter"
    assert pair.intersects is True
    assert pair.spans_overlap is True
    assert pair.combined_span == 13


def test_crossing_spans_do_not_require_letter_intersection() -> None:
    pair = compare_match_pair(
        _match("ABC", 5, (10, 15, 20)),
        _match("XYZ", 5, (12, 17, 22)),
    )

    assert pair.minimum_letter_distance == 2
    assert pair.shared_letter_count == 0
    assert pair.relationship == "crossing"
    assert pair.intersects is False
    assert pair.spans_overlap is True


def test_disjoint_spans_report_distance_and_combined_span() -> None:
    pair = compare_match_pair(
        _match("AB", 5, (10, 15)),
        _match("XY", -5, (30, 25)),
    )

    assert pair.start_distance == 20
    assert pair.minimum_letter_distance == 10
    assert pair.combined_span == 20
    assert pair.relationship == "disjoint"
    assert pair.spans_overlap is False


def test_pairs_are_sorted_deterministically_and_filtered() -> None:
    left = (
        _match("AB", 4, (0, 4)),
        _match("AB", -2, (20, 18)),
    )
    right = (
        _match("XY", 3, (7, 10)),
        _match("XY", 1, (30, 31)),
    )

    pairs = pair_els_matches(left, right, max_distance=5)

    assert [(pair.left.start_index, pair.right.start_index) for pair in pairs] == [
        (0, 7),
    ]


def test_relationship_filters_can_select_disjoint_pairs() -> None:
    left = (_match("AB", 2, (10, 12)),)
    right = (
        _match("XY", 2, (12, 14)),
        _match("XY", 2, (11, 13)),
        _match("XY", 2, (20, 22)),
    )

    pairs = pair_els_matches(
        left,
        right,
        exclude_shared_letters=True,
        exclude_crossing=True,
    )

    assert len(pairs) == 1
    assert pairs[0].relationship == "disjoint"
    assert pairs[0].right.start_index == 20


def test_max_span_and_literal_filters_are_applied() -> None:
    left = (
        _match("AB", 1, (0, 1)),
        _match("AB", 2, (10, 12)),
    )
    right = (
        _match("XY", 1, (5, 6)),
        _match("XY", -1, (20, 19)),
    )

    pairs = pair_els_matches(
        left,
        right,
        max_span=6,
        literal_left=True,
        literal_right=True,
    )

    assert len(pairs) == 1
    assert pairs[0].left.skip == 1
    assert pairs[0].right.skip == 1
    assert pairs[0].combined_span == 6


def test_invalid_max_span_is_rejected() -> None:
    with pytest.raises(ValueError, match="max_span"):
        pair_els_matches((), (), max_span=-1)


def test_same_word_excludes_self_pairs_and_mirrored_duplicates() -> None:
    matches = (
        _match("AB", 1, (0, 1)),
        _match("AB", 1, (5, 6)),
        _match("AB", -1, (10, 9)),
    )

    pairs = pair_els_matches(matches, matches, same_word=True)

    assert len(pairs) == 3
    assert all(pair.left is not pair.right for pair in pairs)


def test_empty_match_sets_return_no_pairs() -> None:
    assert pair_els_matches((), ()) == ()
