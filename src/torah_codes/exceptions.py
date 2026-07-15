"""Application-specific exceptions."""


class TorahCodesError(Exception):
    """Base exception for Torah Codes errors."""


class ConfigurationError(TorahCodesError):
    """Raised when a mapping or configuration file is invalid."""


class CorpusError(TorahCodesError):
    """Raised when the Torah corpus is missing or malformed."""


class VerseParseError(CorpusError):
    """Raised when a verse line cannot be parsed safely."""
