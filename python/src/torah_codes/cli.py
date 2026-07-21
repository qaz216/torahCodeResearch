"""Command-line interface for Torah corpus and ELS analysis."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from torah_codes.corpus.loader import load_torah
from torah_codes.corpus.models import TorahCorpus
from torah_codes.corpus.validation import summarize_corpus
from torah_codes.els import ELSMatch, find_best_els, find_els, find_els_range
from torah_codes.exceptions import TorahCodesError


def _resolve_skip_range(args: argparse.Namespace) -> tuple[int, int]:
    """Resolve exact-skip and range-search command-line options."""

    if args.skip is not None:
        if args.min_skip is not None or args.max_skip is not None:
            raise ValueError("--skip cannot be combined with --min-skip or --max-skip")
        return args.skip, args.skip

    if args.min_skip is None and args.max_skip is None:
        raise ValueError("provide --skip, --max-skip, or both --min-skip and --max-skip")

    if args.min_skip is None:
        if args.max_skip is None or args.max_skip <= 0:
            raise ValueError("--max-skip by itself must be greater than zero")
        return -args.max_skip, args.max_skip

    if args.max_skip is None:
        raise ValueError("--min-skip requires --max-skip")

    return args.min_skip, args.max_skip


def _format_search_description(min_skip: int, max_skip: int) -> str:
    if min_skip == max_skip:
        return f"skip={min_skip:+d}"
    return f"skips={min_skip:+d}..{max_skip:+d}"


def _print_summary(
    *,
    matches: tuple[ELSMatch, ...],
    word: str,
    scope: str,
    min_skip: int,
    max_skip: int,
) -> None:
    counts = Counter(match.skip for match in matches)
    print(
        f"word={word} {_format_search_description(min_skip, max_skip)} "
        f"scope={scope} matches={len(matches)}"
    )
    print("\nskip  matches")
    print("----  -------")
    for skip in range(min_skip, max_skip + 1):
        if skip != 0:
            print(f"{skip:+4d}  {counts[skip]:>7}")
    print(f"\ntotal={len(matches)}")


def _print_match(
    *,
    corpus: TorahCorpus,
    match: ELSMatch,
    match_number: int,
    book_range: range | None,
) -> None:
    print(f"\nmatch {match_number}: skip={match.skip:+d} span={match.span}")
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


def _print_matches(
    *,
    corpus: TorahCorpus,
    matches: tuple[ELSMatch, ...],
    word: str,
    scope: str,
    book_range: range | None,
    min_skip: int,
    max_skip: int,
    limit: int | None,
) -> None:
    print(
        f"word={word} {_format_search_description(min_skip, max_skip)} "
        f"scope={scope} matches={len(matches)}"
    )

    displayed_matches = matches if limit is None else matches[:limit]
    for match_number, match in enumerate(displayed_matches, start=1):
        _print_match(
            corpus=corpus,
            match=match,
            match_number=match_number,
            book_range=book_range,
        )

    hidden_count = len(matches) - len(displayed_matches)
    if hidden_count > 0:
        print(f"\n... {hidden_count} additional matches not shown")


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
    els_parser.add_argument("--skip", type=int, help="Search one signed letter skip")
    els_parser.add_argument(
        "--min-skip",
        type=int,
        help="Minimum signed skip for an inclusive range",
    )
    els_parser.add_argument(
        "--max-skip",
        type=int,
        help="Maximum signed skip, or symmetric range when used alone",
    )
    els_parser.add_argument(
        "--book",
        choices=("GEN", "EXO", "LEV", "NUM", "DEU"),
        help="Restrict the search to one book",
    )
    els_parser.add_argument(
        "--summary",
        action="store_true",
        help="Show match counts by skip without detailed occurrences",
    )
    els_parser.add_argument(
        "--best",
        action="store_true",
        help="Show only the minimum-absolute-skip occurrence",
    )
    els_parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of detailed matches to display",
    )

    args = parser.parse_args()

    try:
        if args.limit is not None and args.limit < 0:
            raise ValueError("--limit must be zero or greater")
        if args.summary and args.best:
            raise ValueError("--summary cannot be combined with --best")

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

        min_skip, max_skip = _resolve_skip_range(args)
        matches: tuple[ELSMatch, ...]
        if args.best:
            best_match = find_best_els(
                corpus,
                args.word,
                min_skip,
                max_skip,
                book_code=args.book,
            )
            matches = () if best_match is None else (best_match,)
        elif min_skip == max_skip:
            matches = find_els(corpus, args.word, min_skip, book_code=args.book)
        else:
            matches = find_els_range(
                corpus,
                args.word,
                min_skip,
                max_skip,
                book_code=args.book,
            )
    except (TorahCodesError, KeyError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")

    scope = args.book or "TORAH"
    book_range = corpus.range_for_book(args.book) if args.book else None

    if args.summary:
        _print_summary(
            matches=matches,
            word=args.word,
            scope=scope,
            min_skip=min_skip,
            max_skip=max_skip,
        )
    else:
        _print_matches(
            corpus=corpus,
            matches=matches,
            word=args.word,
            scope=scope,
            book_range=book_range,
            min_skip=min_skip,
            max_skip=max_skip,
            limit=args.limit,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
