"""Immutable domain models for the Torah corpus."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class BookDefinition:
    """Canonical identity and source filename for one book of the Torah."""

    name: str
    code: str
    filename: str


@dataclass(frozen=True, slots=True, order=True)
class VerseReference:
    """Canonical book/chapter/verse reference."""

    book_index: int
    chapter: int
    verse: int
    book_code: str

    def __str__(self) -> str:
        return f"{self.book_code} {self.chapter:03d}:{self.verse:03d}"


@dataclass(frozen=True, slots=True)
class Verse:
    """A parsed source verse before corpus-wide normalization."""

    reference: VerseReference
    raw_text: str
    source_line_number: int


@dataclass(frozen=True, slots=True)
class LetterPosition:
    """Provenance for one letter in the normalized Torah stream."""

    global_index: int
    character: str
    reference: VerseReference
    verse_letter_index: int
    raw_text_index: int


@dataclass(frozen=True, slots=True)
class TorahCorpus:
    """Immutable normalized Torah text and indexes."""

    verses: tuple[Verse, ...]
    text: str
    positions: tuple[LetterPosition, ...]
    book_ranges: Mapping[str, range]
    verse_ranges: Mapping[VerseReference, range]

    @classmethod
    def create(
        cls,
        *,
        verses: Sequence[Verse],
        text: str,
        positions: Sequence[LetterPosition],
        book_ranges: Mapping[str, range],
        verse_ranges: Mapping[VerseReference, range],
    ) -> TorahCorpus:
        return cls(
            verses=tuple(verses),
            text=text,
            positions=tuple(positions),
            book_ranges=MappingProxyType(dict(book_ranges)),
            verse_ranges=MappingProxyType(dict(verse_ranges)),
        )

    def __len__(self) -> int:
        return len(self.text)

    def letter_at(self, index: int) -> str:
        return self.text[index]

    def position_at(self, index: int) -> LetterPosition:
        return self.positions[index]

    def range_for_book(self, book_code: str) -> range:
        return self.book_ranges[book_code]

    def range_for_verse(self, reference: VerseReference) -> range:
        return self.verse_ranges[reference]
