"""
MoltLang translation module.

This module provides bidirectional translation between English (and other human languages)
and MoltLang, the AI-optimized language.
"""

from dataclasses import dataclass
from typing import Any

from moltlang.config import MoltConfig, get_config
from moltlang.tokens import Token, TokenSequence, TokenType


@dataclass
class TranslationResult:
    """
    Result of a translation operation.

    Attributes:
        text: The translated text
        tokens: Token sequence (for MoltLang output)
        token_count: Number of tokens used
        confidence: Translation confidence score (0.0-1.0)
        original_token_count: Original token count (for efficiency calculation)
    """

    text: str
    tokens: TokenSequence | None = None
    token_count: int = 0
    confidence: float = 0.0
    original_token_count: int = 0

    @property
    def token_efficiency(self) -> float:
        """Calculate token efficiency (reduction percentage)."""
        if self.original_token_count == 0:
            return 0.0
        return 1.0 - (self.token_count / self.original_token_count)

    def __str__(self) -> str:
        """Return the translated text."""
        return self.text


class MoltTranslator:
    """
    Translator for MoltLang.

    Handles bidirectional translation between human languages and MoltLang.
    """

    def __init__(self, config: MoltConfig | None = None):
        """
        Initialize the translator.

        Args:
            config: Optional configuration. Uses default if not provided.
        """
        self.config = config or get_config()
        self._translation_cache: dict[str, TranslationResult] = {}

    def translate_to_molt(
        self, text: str, config: MoltConfig | None = None
    ) -> TranslationResult:
        """
        Translate human language text to MoltLang.

        Args:
            text: Human language text to translate
            config: Optional configuration override

        Returns:
            TranslationResult containing the MoltLang translation

        Examples:
            >>> translator = MoltTranslator()
            >>> result = translator.translate_to_molt("Fetch data from API")
            >>> print(result.text)
            [OP:FETCH][SRC:API]
        """
        cfg = config or self.config

        # Check cache
        if cfg.enable_cache and text in self._translation_cache:
            return self._translation_cache[text]

        # Tokenize input
        original_tokens = self._count_word_tokens(text)

        # Analyze and translate
        tokens = self._analyze_and_translate(text)

        # Build result
        result = TranslationResult(
            text=str(tokens),
            tokens=tokens,
            token_count=len(tokens),
            confidence=self._calculate_confidence(text, tokens),
            original_token_count=original_tokens,
        )

        # Cache result
        if cfg.enable_cache:
            self._translation_cache[text] = result

        return result

    def translate_from_molt(
        self, molt_text: str, config: MoltConfig | None = None
    ) -> TranslationResult:
        """
        Translate MoltLang to human language text.

        Args:
            molt_text: MoltLang text to translate
            config: Optional configuration override

        Returns:
            TranslationResult containing the human language translation

        Examples:
            >>> translator = MoltTranslator()
            >>> result = translator.translate_from_molt("[OP:FETCH][SRC:API]")
            >>> print(result.text)
            Fetch data from API
        """
        cfg = config or self.config

        # Parse MoltLang tokens
        tokens = self._parse_molt_tokens(molt_text)

        # Generate human language translation
        translation = self._generate_human_translation(tokens, cfg.human_language)

        return TranslationResult(
            text=translation,
            tokens=tokens,
            token_count=len(tokens),
            confidence=self._calculate_confidence(translation, tokens),
        )

    def _count_word_tokens(self, text: str) -> int:
        """Count word tokens in text."""
        return len(text.split())

    def _analyze_and_translate(self, text: str) -> TokenSequence:
        """
        Analyze human text and generate MoltLang tokens.

        LLM-Friendly: Supports multiple operations, modifiers, and parameters.
        Example: "Asynchronously fetch and aggregate" -> [MOD:async][OP:fetch][OP:aggregate][SRC:...]

        This is a simplified implementation for the MVP.
        A full implementation would use NLP/LLM-based analysis.
        """
        tokens = TokenSequence()
        text_lower = text.lower()

        # MODIFIER detection - apply to all operations
        if any(word in text_lower for word in ["async", "asynchronous", "asyncronously"]):
            tokens.add(Token(type=TokenType.MOD_ASYNC))
        if any(word in text_lower for word in ["parallel", "concurrent", "simultaneous"]):
            tokens.add(Token(type=TokenType.MOD_PARALLEL))
        if any(word in text_lower for word in ["batch", "bulk", "multiple"]):
            tokens.add(Token(type=TokenType.MOD_BATCH))
        if any(word in text_lower for word in ["cache", "cached", "caching"]):
            tokens.add(Token(type=TokenType.MOD_CACHED))

        # Operation detection - support MULTIPLE operations
        if any(word in text_lower for word in ["fetch", "get", "retrieve", "download"]):
            tokens.add(Token(type=TokenType.OP_FETCH))
        if any(word in text_lower for word in ["parse", "analyze", "extract"]):
            tokens.add(Token(type=TokenType.OP_PARSE))
        if any(word in text_lower for word in ["transform", "convert", "change"]):
            tokens.add(Token(type=TokenType.OP_TRANSFORM))
        if any(word in text_lower for word in ["search", "find", "lookup"]):
            tokens.add(Token(type=TokenType.OP_SEARCH))
        if any(word in text_lower for word in ["validate", "verify", "check"]):
            tokens.add(Token(type=TokenType.OP_VALIDATE))
        if any(word in text_lower for word in ["filter", "sift", "screen"]):
            tokens.add(Token(type=TokenType.OP_FILTER))
        if any(word in text_lower for word in ["aggregate", "combine", "merge", "summarize"]):
            tokens.add(Token(type=TokenType.OP_AGGREGATE))

        # Default to COMPUTE if no operation found
        if len(tokens) == 0:
            tokens.add(Token(type=TokenType.OP_COMPUTE))

        # Source detection (typically only one source)
        if any(word in text_lower for word in ["api", "endpoint", "rest", "graphql"]):
            tokens.add(Token(type=TokenType.SRC_API))
        elif any(word in text_lower for word in ["database", "db", "sql", "nosql"]):
            tokens.add(Token(type=TokenType.SRC_DB))
        elif any(word in text_lower for word in ["file", "document", "csv", "json"]):
            tokens.add(Token(type=TokenType.SRC_FILE))
        elif any(word in text_lower for word in ["memory", "cache", "ram"]):
            tokens.add(Token(type=TokenType.SRC_MEM))

        # Parameter detection - extract values with regex
        import re
        timeout_match = re.search(r'timeout\s*(?:of|:)?\s*(\d+)', text_lower)
        if timeout_match:
            timeout_value = timeout_match.group(1)
            tokens.add(Token(type=TokenType.PARAM_TIMEOUT, value=timeout_value))

        # Return type detection (typically only one return type)
        if any(word in text_lower for word in ["json", "object"]):
            tokens.add(Token(type=TokenType.RET_JSON))
        elif any(word in text_lower for word in ["text", "string", "plain"]):
            tokens.add(Token(type=TokenType.RET_TEXT))
        elif any(word in text_lower for word in ["boolean", "bool", "true", "false"]):
            tokens.add(Token(type=TokenType.RET_BOOL))
        elif any(word in text_lower for word in ["number", "numeric", "int", "float"]):
            tokens.add(Token(type=TokenType.RET_NUM))
        elif any(word in text_lower for word in ["list", "array"]):
            tokens.add(Token(type=TokenType.RET_LIST))
        elif any(word in text_lower for word in ["dict", "map", "hash"]):
            tokens.add(Token(type=TokenType.RET_DICT))

        return tokens

    def _parse_molt_tokens(self, molt_text: str) -> TokenSequence:
        """
        Parse MoltLang text into tokens.

        LLM-friendly: Case-insensitive parsing for flexibility.
        Accepts both [RET:JSON] and [RET:json] - normalizes to enum values.

        Args:
            molt_text: MoltLang string representation

        Returns:
            TokenSequence containing parsed tokens
        """
        tokens = TokenSequence()
        import re

        # Find all token patterns like [TYPE:VALUE] - case-insensitive
        pattern = r"\[([a-zA-Z]+):([a-zA-Z_0-9]+)(?:=([^\]]+))?\]"
        matches = re.findall(pattern, molt_text)

        for category, value, param in matches:
            # Normalize to uppercase for enum lookup
            token_type_str = f"{category.upper()}_{value.upper()}"
            try:
                token_type = TokenType[token_type_str]
                token = Token(type=token_type, value=param if param else None)
                tokens.add(token)
            except KeyError:
                # Unknown token type, skip or handle as custom
                pass

        return tokens

    def _generate_human_translation(
        self, tokens: TokenSequence, target_language: str = "en"
    ) -> str:
        """
        Generate human language translation from MoltLang tokens.

        Args:
            tokens: TokenSequence to translate
            target_language: Target human language (default: English)

        Returns:
            Human language translation
        """
        parts: list[str] = []

        for token in tokens.tokens:
            # Operation translations
            if token.type == TokenType.OP_FETCH:
                parts.append("Fetch")
            elif token.type == TokenType.OP_PARSE:
                parts.append("Parse")
            elif token.type == TokenType.OP_TRANSFORM:
                parts.append("Transform")
            elif token.type == TokenType.OP_SEARCH:
                parts.append("Search")
            elif token.type == TokenType.OP_VALIDATE:
                parts.append("Validate")
            elif token.type == TokenType.OP_FILTER:
                parts.append("Filter")
            elif token.type == TokenType.OP_COMPUTE:
                parts.append("Compute")

            # Source translations
            elif token.type == TokenType.SRC_API:
                parts.append("data from API")
            elif token.type == TokenType.SRC_DB:
                parts.append("data from database")
            elif token.type == TokenType.SRC_FILE:
                parts.append("data from file")
            elif token.type == TokenType.SRC_MEM:
                parts.append("data from memory")

            # Return type translations
            elif token.type == TokenType.RET_JSON:
                parts.append("return JSON")
            elif token.type == TokenType.RET_TEXT:
                parts.append("return text")
            elif token.type == TokenType.RET_BOOL:
                parts.append("return boolean")
            elif token.type == TokenType.RET_NUM:
                parts.append("return number")
            elif token.type == TokenType.RET_LIST:
                parts.append("return list")
            elif token.type == TokenType.RET_DICT:
                parts.append("return dictionary")

        return " ".join(parts) if parts else "Empty operation"

    def _calculate_confidence(self, original: str, tokens: TokenSequence) -> float:
        """
        Calculate translation confidence score.

        Args:
            original: Original text
            tokens: Translated token sequence

        Returns:
            Confidence score (0.0-1.0)
        """
        # Simple heuristic: more tokens matched = higher confidence
        if len(tokens) == 0:
            return 0.0
        if len(tokens) >= 3:
            return 0.95
        if len(tokens) >= 2:
            return 0.85
        return 0.7


# Convenience functions for direct usage

_translator_instance: MoltTranslator | None = None


def _get_translator() -> MoltTranslator:
    """Get or create the shared translator instance."""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = MoltTranslator()
    return _translator_instance


def translate_to_molt(text: str, config: MoltConfig | None = None) -> str:
    """
    Translate human language text to MoltLang.

    This is a convenience function that uses a shared translator instance.

    Args:
        text: Human language text to translate
        config: Optional configuration override

    Returns:
        MoltLang string representation

    Examples:
        >>> from moltlang import translate_to_molt
        >>> molt = translate_to_molt("Fetch data from API and return JSON")
        >>> print(molt)
        [OP:FETCH][SRC:API][RET:JSON]
    """
    translator = _get_translator()
    result = translator.translate_to_molt(text, config)
    return result.text


def translate_from_molt(molt_text: str, config: MoltConfig | None = None) -> str:
    """
    Translate MoltLang to human language text.

    This is a convenience function that uses a shared translator instance.

    Args:
        molt_text: MoltLang text to translate
        config: Optional configuration override

    Returns:
        Human language translation

    Examples:
        >>> from moltlang import translate_from_molt
        >>> english = translate_from_molt("[OP:FETCH][SRC:API][RET:JSON]")
        >>> print(english)
        Fetch data from API return JSON
    """
    translator = _get_translator()
    result = translator.translate_from_molt(molt_text, config)
    return result.text
