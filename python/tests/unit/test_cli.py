"""Tests for ELS CLI argument behavior."""

import argparse

import pytest

from torah_codes.cli import _resolve_skip_range


def _args(
    *,
    skip: int | None = None,
    min_skip: int | None = None,
    max_skip: int | None = None,
) -> argparse.Namespace:
    return argparse.Namespace(skip=skip, min_skip=min_skip, max_skip=max_skip)


def test_resolves_exact_skip() -> None:
    assert _resolve_skip_range(_args(skip=50)) == (50, 50)


def test_resolves_explicit_range() -> None:
    assert _resolve_skip_range(_args(min_skip=-25, max_skip=50)) == (-25, 50)


def test_resolves_symmetric_max_skip() -> None:
    assert _resolve_skip_range(_args(max_skip=50)) == (-50, 50)


def test_rejects_conflicting_exact_and_range_options() -> None:
    with pytest.raises(ValueError, match="cannot be combined"):
        _resolve_skip_range(_args(skip=50, max_skip=100))


def test_rejects_missing_max_skip() -> None:
    with pytest.raises(ValueError, match="requires --max-skip"):
        _resolve_skip_range(_args(min_skip=-50))
