"""Tests for ELS proximity analysis."""

from torah_codes.els import ELSMatch
from torah_codes.proximity import compare_match_pair, pair_els_matches


def _match(word: str, skip: int, indices: tuple[int, ...]) -> ELSMatch:
    return ELSMatch(word=word, skip=skip, indices=indices, positions=())


def test_intersecting_sequences_have_zero_distance() -> None:
    pair = compare_match_pair(
        _match("ABC", 5, (10, 15, 20)),
        _match("XYZ", -3, (23, 20, 17)),
    )

    assert pair.minimum_letter_distance == 0
    assert pair.intersects is True
    assert pair.spans_overlap is True
    assert pair.combined_span == 13


def test_overlapping_spans_do_not_require_letter_intersection() -> None:
    pair = compare_match_pair(
        _match("ABC", 5, (10, 15, 20)),
        _match("XYZ", 5, (12, 17, 22)),
    )

    assert pair.minimum_letter_distance == 2
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
