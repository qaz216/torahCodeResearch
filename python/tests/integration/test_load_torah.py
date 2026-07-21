from pathlib import Path

from torah_codes.corpus.loader import load_torah

PROJECT_ROOT = Path(__file__).resolve().parents[3]

def test_loads_books_in_canonical_order() -> None:
    corpus = load_torah(PROJECT_ROOT)

    assert str(corpus.verses[0].reference) == "GEN 001:001"
    assert str(corpus.verses[-1].reference) == "DEU 034:012"
    assert corpus.text.startswith("BRASYT")
    assert corpus.text.endswith("LOYNYKLYsRAL")


def test_position_index_maps_back_to_source() -> None:
    corpus = load_torah(PROJECT_ROOT)
    first = corpus.position_at(0)

    assert first.character == "B"
    assert str(first.reference) == "GEN 001:001"
    assert first.verse_letter_index == 0
    assert first.raw_text_index == 0
