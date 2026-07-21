"""Tests for ELS searching."""

import pytest

from torah_codes.els import find_els_indices, iter_signed_skips


def test_finds_forward_els() -> None:
    text = "T" + ("x" * 49) + "V" + ("x" * 49) + "R" + ("x" * 49) + "H"

    assert find_els_indices(text, "TVRH", 50) == ((0, 50, 100, 150),)


def test_finds_backward_els() -> None:
    text = "H" + ("x" * 49) + "R" + ("x" * 49) + "V" + ("x" * 49) + "T"

    assert find_els_indices(text, "TVRH", -50) == ((150, 100, 50, 0),)


def test_book_scope_prevents_boundary_crossing() -> None:
    text = "TxxVxxRxxH"

    assert find_els_indices(text, "TVRH", 3, search_range=range(0, 9)) == ()
    assert find_els_indices(text, "TVRH", 3, search_range=range(0, 10)) == (
        (0, 3, 6, 9),
    )


def test_signed_skip_range_excludes_zero() -> None:
    assert tuple(iter_signed_skips(-2, 2)) == (-2, -1, 1, 2)


def test_signed_skip_range_can_be_one_direction() -> None:
    assert tuple(iter_signed_skips(2, 4)) == (2, 3, 4)


def test_rejects_reversed_skip_range() -> None:
    with pytest.raises(
        ValueError,
        match="min_skip must be less than or equal to max_skip",
    ):
        tuple(iter_signed_skips(5, -5))


@pytest.mark.parametrize(
    ("word", "skip", "message"),
    (
        ("", 1, "word must not be empty"),
        ("TVRH", 0, "skip must not be zero"),
    ),
)
def test_rejects_invalid_search(word: str, skip: int, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        find_els_indices("TVRH", word, skip)
