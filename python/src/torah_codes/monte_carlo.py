"""Reproducible Monte Carlo controls for ELS searches."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from random import Random

from torah_codes.corpus.models import TorahCorpus
from torah_codes.els_statistics import calculate_els_statistics


@dataclass(frozen=True, slots=True)
class MonteCarloSample:
    """One generated control word and its ELS measurements."""

    word: str
    total_matches: int
    best_absolute_skip: int | None


@dataclass(frozen=True, slots=True)
class MonteCarloResult:
    """Observed ELS measurements compared with generated control words."""

    word: str
    iterations: int
    seed: int
    min_skip: int
    max_skip: int
    observed_total_matches: int
    observed_best_absolute_skip: int | None
    samples: tuple[MonteCarloSample, ...]
    total_matches_p_value: float
    best_skip_p_value: float | None


def weighted_alphabet(text: str) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Return letters and integer weights derived from corpus frequencies."""

    if not text:
        raise ValueError("control text must not be empty")

    counts = Counter(text)
    letters = tuple(sorted(counts))
    weights = tuple(counts[letter] for letter in letters)
    return letters, weights


def generate_control_words(
    text: str,
    length: int,
    iterations: int,
    *,
    seed: int,
) -> tuple[str, ...]:
    """Generate reproducible words from corpus-weighted letter frequencies."""

    if length <= 0:
        raise ValueError("word length must be greater than zero")
    if iterations <= 0:
        raise ValueError("iterations must be greater than zero")

    letters, weights = weighted_alphabet(text)
    random = Random(seed)

    return tuple(
        "".join(random.choices(letters, weights=weights, k=length))
        for _ in range(iterations)
    )


def empirical_upper_tail(observed: int, controls: tuple[int, ...]) -> float:
    """Return a plus-one corrected upper-tail empirical p-value."""

    extreme = sum(value >= observed for value in controls)
    return (extreme + 1) / (len(controls) + 1)


def empirical_lower_tail(observed: int, controls: tuple[int, ...]) -> float:
    """Return a plus-one corrected lower-tail empirical p-value."""

    extreme = sum(value <= observed for value in controls)
    return (extreme + 1) / (len(controls) + 1)


def run_monte_carlo(
    corpus: TorahCorpus,
    word: str,
    min_skip: int,
    max_skip: int,
    *,
    iterations: int,
    seed: int,
    book_code: str | None = None,
) -> MonteCarloResult:
    """Compare a word with corpus-frequency-weighted random controls."""

    normalized_word = word.strip()
    if not normalized_word:
        raise ValueError("word must not be empty")

    scope_range = (
        corpus.range_for_book(book_code.upper()) if book_code is not None else None
    )
    control_text = (
        corpus.text[scope_range.start : scope_range.stop]
        if scope_range is not None
        else corpus.text
    )

    observed = calculate_els_statistics(
        corpus,
        normalized_word,
        min_skip,
        max_skip,
        book_code=book_code,
    )
    control_words = generate_control_words(
        control_text,
        len(normalized_word),
        iterations,
        seed=seed,
    )

    samples: list[MonteCarloSample] = []
    for control_word in control_words:
        statistics = calculate_els_statistics(
            corpus,
            control_word,
            min_skip,
            max_skip,
            book_code=book_code,
        )
        samples.append(
            MonteCarloSample(
                word=control_word,
                total_matches=statistics.total_matches,
                best_absolute_skip=(
                    abs(statistics.best_match.skip)
                    if statistics.best_match is not None
                    else None
                ),
            )
        )

    sample_tuple = tuple(samples)
    total_matches_p_value = empirical_upper_tail(
        observed.total_matches,
        tuple(sample.total_matches for sample in sample_tuple),
    )

    observed_best = (
        abs(observed.best_match.skip) if observed.best_match is not None else None
    )
    control_best = tuple(
        sample.best_absolute_skip
        for sample in sample_tuple
        if sample.best_absolute_skip is not None
    )
    best_skip_p_value = (
        empirical_lower_tail(observed_best, control_best)
        if observed_best is not None and control_best
        else None
    )

    return MonteCarloResult(
        word=normalized_word,
        iterations=iterations,
        seed=seed,
        min_skip=min_skip,
        max_skip=max_skip,
        observed_total_matches=observed.total_matches,
        observed_best_absolute_skip=observed_best,
        samples=sample_tuple,
        total_matches_p_value=total_matches_p_value,
        best_skip_p_value=best_skip_p_value,
    )
