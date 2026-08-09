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

## Display a verse in Hebrew

Use the `verse` command with a global, one-based verse number to select a verse
from the full Torah in canonical order. The validated corpus contains 5,852
verses, so the accepted range is `1` through `5852`.

```bash
python -m torah_codes.cli --project-root .. verse 5423
```

The existing book, chapter, and verse form is also supported. Book numbers
follow the canonical Torah order: Genesis `1`, Exodus `2`, Leviticus `3`,
Numbers `4`, and Deuteronomy `5`.

```bash
python -m torah_codes.cli --project-root .. verse 2:23:1
```

Three-letter book codes are also accepted, either as one colon-delimited value
or as a code followed by a chapter-and-verse value:

```bash
python -m torah_codes.cli --project-root .. verse EXO:23:1
python -m torah_codes.cli --project-root .. verse EXO 23:1
```

Hebrew is the default output format. It preserves the source verse's spaces,
hyphens, and punctuation. The source corpus is consonantal, so the Hebrew output
is unpointed and does not include niqqud or cantillation marks.

Use `--letters-only` to print the exact contiguous letter sequence used for ELS
analysis:

```bash
python -m torah_codes.cli --project-root .. verse 2:23:1 --letters-only
```

Use `--format transliteration` to display the canonical source transliteration.
It can be combined with `--letters-only`:

```bash
python -m torah_codes.cli --project-root .. verse 2:23:1 --format transliteration
python -m torah_codes.cli --project-root .. verse 2:23:1 --format transliteration --letters-only
```

For development:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pytest
```
