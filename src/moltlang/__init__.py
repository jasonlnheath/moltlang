"""
MoltLang - A Language for LLMs, by LLMs

This package provides an AI-optimized language for efficient AI-to-AI communication,
with bidirectional translation between MoltLang and human languages (starting with English).

Example usage:
    >>> from moltlang import translate_to_molt, translate_from_molt
    >>> molt = translate_to_molt("Fetch data from API")
    >>> print(molt)
    [OP:FETCH][SRC:API]
    >>> english = translate_from_molt(molt)
    >>> print(english)
    'Fetch data from API'
"""

__version__ = "0.1.0"
__author__ = "Jason"
__license__ = "AGPL-3.0"

from moltlang.translator import translate_to_molt, translate_from_molt, MoltTranslator, TranslationResult
from moltlang.tokens import Token, TokenType, TokenRegistry
from moltlang.validator import validate_translation, MoltValidator, TranslationQuality
from moltlang.config import MoltConfig

__all__ = [
    "translate_to_molt",
    "translate_from_molt",
    "MoltTranslator",
    "MoltValidator",
    "validate_translation",
    "TranslationQuality",
    "Token",
    "TokenType",
    "TokenRegistry",
    "MoltConfig",
    "TranslationResult",
    "translate_to_molt_result",
    "translate_from_molt_result",
]


def translate_to_molt_result(text: str, config: MoltConfig | None = None) -> TranslationResult:
    """
    Translate to MoltLang and return full TranslationResult.

    This is for MCP/bridge usage where metadata is required.
    """
    from moltlang.translator import MoltTranslator

    translator = MoltTranslator()
    return translator.translate_to_molt(text, config)


def translate_from_molt_result(molt_text: str, config: MoltConfig | None = None) -> TranslationResult:
    """
    Translate from MoltLang and return full TranslationResult.

    This is for MCP/bridge usage where metadata is required.
    """
    from moltlang.translator import MoltTranslator

    translator = MoltTranslator()
    return translator.translate_from_molt(molt_text, config)
