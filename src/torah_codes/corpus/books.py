"""Canonical Torah book definitions."""

from torah_codes.corpus.models import BookDefinition

BOOKS: tuple[BookDefinition, ...] = (
    BookDefinition("Genesis", "GEN", "Genesis.txt"),
    BookDefinition("Exodus", "EXO", "Exodus.txt"),
    BookDefinition("Leviticus", "LEV", "Leviticus.txt"),
    BookDefinition("Numbers", "NUM", "Numbers.txt"),
    BookDefinition("Deuteronomy", "DEU", "Deuteronomy.txt"),
)

BOOK_BY_CODE = {book.code: book for book in BOOKS}
BOOK_INDEX_BY_CODE = {book.code: index for index, book in enumerate(BOOKS)}
