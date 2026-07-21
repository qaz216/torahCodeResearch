"""Load transliteration and ignored-character mappings from XML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping
from xml.etree import ElementTree

from torah_codes.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class LetterDefinition:
    name: str
    numerical_value: int
    character: str


@dataclass(frozen=True, slots=True)
class Alphabet:
    letters: Mapping[str, LetterDefinition]
    skipped_characters: frozenset[str]

    def is_letter(self, character: str) -> bool:
        return character in self.letters

    def is_skipped(self, character: str) -> bool:
        return character in self.skipped_characters


def load_alphabet(letters_path: Path, skip_characters_path: Path) -> Alphabet:
    letters = _load_letters(letters_path)
    skipped = _load_skipped_characters(skip_characters_path)

    overlap = set(letters).intersection(skipped)
    if overlap:
        chars = ", ".join(repr(value) for value in sorted(overlap))
        raise ConfigurationError(f"Characters cannot be both letters and skipped: {chars}")

    return Alphabet(MappingProxyType(letters), frozenset(skipped))


def _load_letters(path: Path) -> dict[str, LetterDefinition]:
    root = _parse_xml(path)
    if root.tag != "letters":
        raise ConfigurationError(f"Expected <letters> root in {path}")

    result: dict[str, LetterDefinition] = {}
    for element in root.findall("letter"):
        name = _required_attribute(element, "name", path)
        numerical = element.find("numerical_value")
        translation = element.find("character_translation")
        if numerical is None or translation is None:
            raise ConfigurationError(f"Incomplete letter definition {name!r} in {path}")

        numerical_text = _required_attribute(numerical, "value", path)
        character = _required_attribute(translation, "value", path)
        if len(character) != 1:
            raise ConfigurationError(
                f"Letter {name!r} must map to exactly one character, got {character!r}"
            )

        try:
            numerical_value = int(numerical_text)
        except ValueError as exc:
            raise ConfigurationError(
                f"Invalid numerical value {numerical_text!r} for letter {name!r}"
            ) from exc

        # The legacy XML intentionally contains multiple Hebrew names for the
        # same transliteration character (for example caf/chaf -> K). Preserve
        # the first definition, matching the effective character-based model.
        result.setdefault(character, LetterDefinition(name, numerical_value, character))

    if not result:
        raise ConfigurationError(f"No letters were loaded from {path}")
    return result


def _load_skipped_characters(path: Path) -> set[str]:
    root = _parse_xml(path)
    if root.tag != "skip_characters":
        raise ConfigurationError(f"Expected <skip_characters> root in {path}")

    result: set[str] = set()
    for element in root.findall("character"):
        value = element.get("name")
        if value is None:
            raise ConfigurationError(f"Missing character name in {path}")
        if len(value) != 1:
            raise ConfigurationError(f"Skipped character must have length one, got {value!r}")
        result.add(value)

    return result


def _parse_xml(path: Path) -> ElementTree.Element:
    if not path.is_file():
        raise ConfigurationError(f"Configuration file does not exist: {path}")
    try:
        return ElementTree.parse(path).getroot()
    except ElementTree.ParseError as exc:
        raise ConfigurationError(f"Invalid XML in {path}: {exc}") from exc


def _required_attribute(element: ElementTree.Element, name: str, path: Path) -> str:
    value = element.get(name)
    if value is None or value == "":
        raise ConfigurationError(f"Missing {name!r} attribute in {path}")
    return value
