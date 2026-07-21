# Torah Code Research

A modern Python research platform for validating the Torah corpus and studying
Equidistant Letter Sequences (ELS) and related statistical questions.

## Current milestone

Phase 1 establishes a strict, immutable, fully indexed Torah corpus:

- canonical book order;
- strict verse parsing;
- XML-driven transliteration and skipped-character handling;
- rejection of unknown characters;
- global letter-to-verse provenance;
- per-book and whole-corpus counts and SHA-256 checksums.

## Run corpus validation

```bash
python -m torah_codes.cli --project-root . validate
```

For development:

```bash
python -m pip install -e '.[dev]'
pytest
```
