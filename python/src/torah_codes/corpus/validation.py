"""Structured validation summaries for a loaded Torah corpus."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib

from torah_codes.corpus.books import BOOKS
from torah_codes.corpus.models import TorahCorpus


@dataclass(frozen=True, slots=True)
class BookSummary:
    name: str
    code: str
    verses: int
    letters: int
    sha256: str


@dataclass(frozen=True, slots=True)
class CorpusSummary:
    books: tuple[BookSummary, ...]
    verses: int
    letters: int
    sha256: str


def summarize_corpus(corpus: TorahCorpus) -> CorpusSummary:
    verse_counts = Counter(verse.reference.book_code for verse in corpus.verses)
    books: list[BookSummary] = []

    for book in BOOKS:
        book_range = corpus.range_for_book(book.code)
        text = corpus.text[book_range.start : book_range.stop]
        books.append(
            BookSummary(
                name=book.name,
                code=book.code,
                verses=verse_counts[book.code],
                letters=len(text),
                sha256=_sha256(text),
            )
        )

    return CorpusSummary(
        books=tuple(books),
        verses=len(corpus.verses),
        letters=len(corpus),
        sha256=_sha256(corpus.text),
    )


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()
