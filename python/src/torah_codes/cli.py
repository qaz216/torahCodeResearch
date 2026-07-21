"""Command-line interface for Torah corpus and ELS analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from torah_codes.corpus.loader import load_torah
from torah_codes.corpus.validation import summarize_corpus
from torah_codes.els import find_els
from torah_codes.exceptions import TorahCodesError


def main() -> int:
    parser = argparse.ArgumentParser(prog="torah-codes")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "validate",
        help="Load, validate, and summarize the Torah corpus",
    )

    els_parser = subparsers.add_parser("els", help="Search for an ELS")
    els_parser.add_argument("word", help="Word in canonical transliteration")
    els_parser.add_argument("--skip", type=int, required=True, help="Signed letter skip")
    els_parser.add_argument(
        "--book",
        choices=("GEN", "EXO", "LEV", "NUM", "DEU"),
        help="Restrict the search to one book",
    )

    args = parser.parse_args()

    try:
        corpus = load_torah(args.project_root)

        if args.command == "validate":
            summary = summarize_corpus(corpus)
            for book in summary.books:
                print(
                    f"{book.name:<12} verses={book.verses:>4} "
                    f"letters={book.letters:>6} sha256={book.sha256}"
                )
            print(
                f"{'Torah':<12} verses={summary.verses:>4} "
                f"letters={summary.letters:>6} sha256={summary.sha256}"
            )
            return 0

        matches = find_els(
            corpus,
            args.word,
            args.skip,
            book_code=args.book,
        )
    except (TorahCodesError, KeyError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")

    scope = args.book or "TORAH"
    print(f"word={args.word} skip={args.skip:+d} scope={scope} matches={len(matches)}")

    book_range = corpus.range_for_book(args.book) if args.book else None

    for match_number, match in enumerate(matches, start=1):
        print(f"\nmatch {match_number}:")
        for letter_number, position in enumerate(match.positions, start=1):
            global_position = position.global_index + 1
            book_position = (
                position.global_index - book_range.start + 1
                if book_range is not None
                else None
            )

            location = f"global={global_position}"
            if book_position is not None:
                location += f" book={book_position}"

            print(
                f"  {letter_number}: {position.character} {location} "
                f"verse={position.reference} "
                f"verse-letter={position.verse_letter_index + 1}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
