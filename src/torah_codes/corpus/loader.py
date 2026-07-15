"""Load and normalize the five Torah books in canonical order."""

from __future__ import annotations

from pathlib import Path

from torah_codes.corpus.books import BOOKS
from torah_codes.corpus.mappings import Alphabet, load_alphabet
from torah_codes.corpus.models import LetterPosition, TorahCorpus, Verse, VerseReference
from torah_codes.corpus.parser import parse_verse_line
from torah_codes.exceptions import CorpusError


def load_torah(
    project_root: Path | str = Path("."),
    *,
    bible_directory: Path | str = Path("data/bible"),
    letters_file: Path | str = Path("etc/letters.xml"),
    skip_characters_file: Path | str = Path("etc/skip_characters.xml"),
) -> TorahCorpus:
    root = Path(project_root)
    bible_path = _resolve(root, bible_directory)
    alphabet = load_alphabet(
        _resolve(root, letters_file),
        _resolve(root, skip_characters_file),
    )

    verses: list[Verse] = []
    for book_index, book in enumerate(BOOKS):
        book_path = bible_path / book.filename
        if not book_path.is_file():
            raise CorpusError(f"Missing Torah source file: {book_path}")

        previous: VerseReference | None = None
        with book_path.open("r", encoding="utf-8", newline="") as source:
            for line_number, raw_line in enumerate(source, start=1):
                verse = parse_verse_line(
                    raw_line,
                    expected_book_code=book.code,
                    book_index=book_index,
                    source_line_number=line_number,
                )
                if previous is not None and verse.reference <= previous:
                    raise CorpusError(
                        f"Verse references are not strictly increasing in {book_path}: "
                        f"{previous} then {verse.reference}"
                    )
                verses.append(verse)
                previous = verse.reference

        if previous is None:
            raise CorpusError(f"Torah source file is empty: {book_path}")

    return _normalize(verses, alphabet)


def _normalize(verses: list[Verse], alphabet: Alphabet) -> TorahCorpus:
    characters: list[str] = []
    positions: list[LetterPosition] = []
    verse_ranges: dict[VerseReference, range] = {}
    book_starts: dict[str, int] = {}
    book_ends: dict[str, int] = {}

    for verse in verses:
        book_starts.setdefault(verse.reference.book_code, len(characters))
        verse_start = len(characters)
        verse_letter_index = 0

        for raw_text_index, character in enumerate(verse.raw_text):
            if alphabet.is_skipped(character):
                continue
            if not alphabet.is_letter(character):
                raise CorpusError(
                    f"Undefined character {character!r} at {verse.reference}, "
                    f"source line {verse.source_line_number}, text offset {raw_text_index}"
                )

            global_index = len(characters)
            characters.append(character)
            positions.append(
                LetterPosition(
                    global_index=global_index,
                    character=character,
                    reference=verse.reference,
                    verse_letter_index=verse_letter_index,
                    raw_text_index=raw_text_index,
                )
            )
            verse_letter_index += 1

        verse_ranges[verse.reference] = range(verse_start, len(characters))
        book_ends[verse.reference.book_code] = len(characters)

    book_ranges = {
        code: range(start, book_ends[code]) for code, start in book_starts.items()
    }
    return TorahCorpus.create(
        verses=verses,
        text="".join(characters),
        positions=positions,
        book_ranges=book_ranges,
        verse_ranges=verse_ranges,
    )


def _resolve(root: Path, path: Path | str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate
