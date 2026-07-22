"""Tests for Monte Carlo ELS controls."""

import pytest

from torah_codes.monte_carlo import (
    empirical_lower_tail,
    empirical_upper_tail,
    generate_control_words,
    weighted_alphabet,
)


def test_weighted_alphabet_is_sorted_and_counted() -> None:
    assert weighted_alphabet("ABACA") == (("A", "B", "C"), (3, 1, 1))


def test_control_words_are_reproducible() -> None:
    first = generate_control_words("AAABBC", 4, 5, seed=17)
    second = generate_control_words("AAABBC", 4, 5, seed=17)

    assert first == second
    assert len(first) == 5
    assert all(len(word) == 4 for word in first)


def test_empirical_p_values_use_plus_one_correction() -> None:
    controls = (1, 2, 3, 4)

    assert empirical_upper_tail(3, controls) == pytest.approx(3 / 5)
    assert empirical_lower_tail(2, controls) == pytest.approx(3 / 5)


@pytest.mark.parametrize(
    ("length", "iterations", "message"),
    (
        (0, 10, "word length"),
        (4, 0, "iterations"),
    ),
)
def test_rejects_invalid_generation(
    length: int,
    iterations: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        generate_control_words("ABCD", length, iterations, seed=1)
