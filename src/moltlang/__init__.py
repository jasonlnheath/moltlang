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

from moltlang.translator import translate_to_molt, translate_from_molt
from moltlang.tokens import Token, TokenType, TokenRegistry
from moltlang.validator import validate_translation, TranslationQuality
from moltlang.config import MoltConfig

__all__ = [
    "translate_to_molt",
    "translate_from_molt",
    "validate_translation",
    "TranslationQuality",
    "Token",
    "TokenType",
    "TokenRegistry",
    "MoltConfig",
]
