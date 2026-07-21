"""Equidistant Letter Sequence (ELS) searching."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from torah_codes.corpus.models import LetterPosition, TorahCorpus


@dataclass(frozen=True, slots=True)
class ELSMatch:
    """One occurrence of a word at a fixed signed skip."""

    word: str
    skip: int
    indices: tuple[int, ...]
    positions: tuple[LetterPosition, ...]

    @property
    def start_index(self) -> int:
        return self.indices[0]

    @property
    def end_index(self) -> int:
        return self.indices[-1]

    @property
    def span(self) -> int:
        """Return the distance from the first selected letter to the last."""
        return abs(self.end_index - self.start_index)


def find_els_indices(
    text: str,
    word: str,
    skip: int,
    *,
    search_range: range | None = None,
) -> tuple[tuple[int, ...], ...]:
    """Return all ELS index sequences for ``word`` at the signed ``skip``.

    A skip of 50 means selected letters are 50 positions apart, leaving
    49 intervening letters.

    When ``search_range`` is supplied, every selected index must remain
    within that range.
    """

    if not word:
        raise ValueError("word must not be empty")
    if skip == 0:
        raise ValueError("skip must not be zero")

    scope = search_range if search_range is not None else range(len(text))
    if scope.step != 1:
        raise ValueError("search_range must have a step of 1")

    matches: list[tuple[int, ...]] = []

    for start in scope:
        if text[start] != word[0]:
            continue

        final_index = start + (len(word) - 1) * skip
        if final_index < scope.start or final_index >= scope.stop:
            continue

        indices = tuple(start + offset * skip for offset in range(len(word)))
        if all(text[index] == expected for index, expected in zip(indices, word)):
            matches.append(indices)

    return tuple(matches)


def find_els(
    corpus: TorahCorpus,
    word: str,
    skip: int,
    *,
    book_code: str | None = None,
) -> tuple[ELSMatch, ...]:
    """Search the whole Torah or one canonical book for an ELS."""

    search_range = (
        corpus.range_for_book(book_code.upper()) if book_code is not None else None
    )
    normalized_word = word.strip()

    index_matches = find_els_indices(
        corpus.text,
        normalized_word,
        skip,
        search_range=search_range,
    )

    return tuple(
        ELSMatch(
            word=normalized_word,
            skip=skip,
            indices=indices,
            positions=tuple(corpus.position_at(index) for index in indices),
        )
        for indices in index_matches
    )


def iter_signed_skips(min_skip: int, max_skip: int) -> Iterable[int]:
    """Yield every signed skip in an inclusive range, excluding zero."""

    if min_skip > max_skip:
        raise ValueError("min_skip must be less than or equal to max_skip")

    for skip in range(min_skip, max_skip + 1):
        if skip != 0:
            yield skip


def _match_sort_key(match: ELSMatch) -> tuple[int, int, int]:
    return abs(match.skip), match.skip, match.start_index


def find_els_range(
    corpus: TorahCorpus,
    word: str,
    min_skip: int,
    max_skip: int,
    *,
    book_code: str | None = None,
) -> tuple[ELSMatch, ...]:
    """Search an inclusive range of signed skips, excluding zero.

    Results are ordered by absolute skip, signed skip, and starting index.
    """

    matches = [
        match
        for skip in iter_signed_skips(min_skip, max_skip)
        for match in find_els(corpus, word, skip, book_code=book_code)
    ]

    return tuple(sorted(matches, key=_match_sort_key))


def find_best_els(
    corpus: TorahCorpus,
    word: str,
    min_skip: int,
    max_skip: int,
    *,
    book_code: str | None = None,
) -> ELSMatch | None:
    """Return the deterministic minimum-absolute-skip occurrence.

    Ties are resolved by signed skip and then starting index.
    """

    matches = find_els_range(
        corpus,
        word,
        min_skip,
        max_skip,
        book_code=book_code,
    )
    return matches[0] if matches else None
