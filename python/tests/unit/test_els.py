"""Tests for Equidistant Letter Sequence searching."""

import pytest

from torah_codes.els import find_els_indices


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
