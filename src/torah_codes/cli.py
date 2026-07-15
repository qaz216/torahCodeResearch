"""Command-line interface for corpus validation."""

from __future__ import annotations

import argparse
from pathlib import Path

from torah_codes.corpus.loader import load_torah
from torah_codes.corpus.validation import summarize_corpus
from torah_codes.exceptions import TorahCodesError


def main() -> int:
    parser = argparse.ArgumentParser(prog="torah-codes")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Load, validate, and summarize the Torah corpus")
    args = parser.parse_args()

    try:
        corpus = load_torah(args.project_root)
    except TorahCodesError as exc:
        parser.exit(1, f"error: {exc}\n")

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


if __name__ == "__main__":
    raise SystemExit(main())
