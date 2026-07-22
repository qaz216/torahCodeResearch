"""Command-line interface for Torah corpus and ELS analysis."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from torah_codes.comparison import ELSComparison, compare_els_words
from torah_codes.corpus.loader import load_torah
from torah_codes.corpus.models import TorahCorpus
from torah_codes.corpus.validation import summarize_corpus
from torah_codes.els import ELSMatch, find_best_els, find_els, find_els_range
from torah_codes.els_statistics import ELSStatistics, calculate_els_statistics
from torah_codes.exceptions import TorahCodesError
from torah_codes.monte_carlo import MonteCarloResult, run_monte_carlo


def _add_skip_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--skip", type=int, help="Search one signed letter skip")
    parser.add_argument(
        "--min-skip",
        type=int,
        help="Minimum signed skip for an inclusive range",
    )
    parser.add_argument(
        "--max-skip",
        type=int,
        help="Maximum signed skip, or symmetric range when used alone",
    )
    parser.add_argument(
        "--book",
        choices=("GEN", "EXO", "LEV", "NUM", "DEU"),
        help="Restrict the search to one book",
    )


def _add_search_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("word", help="Word in canonical transliteration")
    _add_skip_arguments(parser)


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


def _format_optional_number(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _print_statistics(
    *,
    statistics: ELSStatistics,
    scope: str,
) -> None:
    print(
        f"word={statistics.word} "
        f"{_format_search_description(statistics.min_skip, statistics.max_skip)} "
        f"scope={scope}"
    )
    print(f"total matches:       {statistics.total_matches}")
    print(f"matched skips:       {statistics.matched_skip_count}")
    print(
        "mean absolute skip:  "
        f"{_format_optional_number(statistics.mean_absolute_skip)}"
    )
    print(
        "median absolute skip:"
        f" {_format_optional_number(statistics.median_absolute_skip)}"
    )

    if statistics.best_match is None:
        print("best occurrence:     none")
    else:
        print(
            "best occurrence:     "
            f"skip={statistics.best_match.skip:+d} "
            f"start={statistics.best_match.start_index + 1} "
            f"span={statistics.best_match.span}"
        )

    peaks = statistics.peak_frequencies
    if not peaks:
        print("peak skip:           none")
    else:
        peak_description = ", ".join(
            f"{frequency.skip:+d} ({frequency.matches})"
            for frequency in peaks
        )
        print(f"peak skip:           {peak_description}")

    print("\nskip  matches")
    print("----  -------")
    for frequency in statistics.frequencies:
        print(f"{frequency.skip:+4d}  {frequency.matches:>7}")



def _format_best_skip(statistics: ELSStatistics) -> str:
    if statistics.best_match is None:
        return "n/a"
    return f"{statistics.best_match.skip:+d}"


def _print_comparison(
    *,
    comparison: ELSComparison,
    scope: str,
) -> None:
    left = comparison.left
    right = comparison.right

    print(
        f"scope={scope} "
        f"{_format_search_description(left.min_skip, left.max_skip)}"
    )
    print()
    print(f"{'metric':<24} {left.word:>12} {right.word:>12}")
    print(f"{'-' * 24} {'-' * 12} {'-' * 12}")
    print(
        f"{'total matches':<24} "
        f"{left.total_matches:>12} {right.total_matches:>12}"
    )
    print(
        f"{'matched skips':<24} "
        f"{left.matched_skip_count:>12} {right.matched_skip_count:>12}"
    )
    print(
        f"{'best skip':<24} "
        f"{_format_best_skip(left):>12} {_format_best_skip(right):>12}"
    )
    print(
        f"{'mean absolute skip':<24} "
        f"{_format_optional_number(left.mean_absolute_skip):>12} "
        f"{_format_optional_number(right.mean_absolute_skip):>12}"
    )
    print(
        f"{'median absolute skip':<24} "
        f"{_format_optional_number(left.median_absolute_skip):>12} "
        f"{_format_optional_number(right.median_absolute_skip):>12}"
    )

    best_difference = comparison.best_absolute_skip_difference
    print()
    print(
        f"match-count ratio:             "
        f"{_format_optional_number(comparison.match_count_ratio)}"
    )
    print(
        "best absolute-skip difference: "
        f"{best_difference if best_difference is not None else 'n/a'}"
    )
    print(f"shared matched skips:          {len(comparison.shared_matched_skips)}")
    if comparison.shared_matched_skips:
        print(
            "shared skip values:           "
            + ", ".join(f"{skip:+d}" for skip in comparison.shared_matched_skips)
        )



def _format_probability(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _print_monte_carlo(result: MonteCarloResult, scope: str) -> None:
    best_skip = result.observed_best_absolute_skip
    print(
        f"word={result.word} "
        f"{_format_search_description(result.min_skip, result.max_skip)} "
        f"scope={scope}"
    )
    print(f"iterations:                  {result.iterations}")
    print(f"seed:                        {result.seed}")
    print(f"observed total matches:      {result.observed_total_matches}")
    print(
        "observed best absolute skip: "
        f"{best_skip if best_skip is not None else 'n/a'}"
    )
    print(
        "p(total matches >= observed): "
        f"{_format_probability(result.total_matches_p_value)}"
    )
    print(
        "p(best skip <= observed):      "
        f"{_format_probability(result.best_skip_p_value)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(prog="torah-codes")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "validate",
        help="Load, validate, and summarize the Torah corpus",
    )

    els_parser = subparsers.add_parser("els", help="Search for an ELS")
    _add_search_arguments(els_parser)
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

    stats_parser = subparsers.add_parser(
        "stats",
        help="Calculate descriptive statistics for an ELS search",
    )
    _add_search_arguments(stats_parser)

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare descriptive ELS statistics for two words",
    )
    compare_parser.add_argument("left_word")
    compare_parser.add_argument("right_word")
    _add_skip_arguments(compare_parser)


    experiment_parser = subparsers.add_parser(
        "experiment",
        help="Run reproducible statistical control experiments",
    )
    experiment_subparsers = experiment_parser.add_subparsers(
        dest="experiment_command",
        required=True,
    )
    monte_carlo_parser = experiment_subparsers.add_parser(
        "monte-carlo",
        help="Compare a word with weighted random control words",
    )
    _add_search_arguments(monte_carlo_parser)
    monte_carlo_parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of random control words (default: 1000)",
    )
    monte_carlo_parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="Random seed for reproducibility (default: 1)",
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

        min_skip, max_skip = _resolve_skip_range(args)
        scope = args.book or "TORAH"


        if args.command == "experiment":
            if args.iterations <= 0:
                raise ValueError("--iterations must be greater than zero")
            result = run_monte_carlo(
                corpus,
                args.word,
                min_skip,
                max_skip,
                iterations=args.iterations,
                seed=args.seed,
                book_code=args.book,
            )
            _print_monte_carlo(result, scope)
            return 0

        if args.command == "stats":
            statistics = calculate_els_statistics(
                corpus,
                args.word,
                min_skip,
                max_skip,
                book_code=args.book,
            )
            _print_statistics(statistics=statistics, scope=scope)
            return 0

        if args.command == "compare":
            comparison = compare_els_words(
                corpus,
                args.left_word,
                args.right_word,
                min_skip,
                max_skip,
                book_code=args.book,
            )
            _print_comparison(comparison=comparison, scope=scope)
            return 0

        if args.limit is not None and args.limit < 0:
            raise ValueError("--limit must be zero or greater")
        if args.summary and args.best:
            raise ValueError("--summary cannot be combined with --best")

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
