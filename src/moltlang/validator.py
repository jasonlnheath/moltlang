"""
MoltLang validation module.

This module provides validation and quality assessment for MoltLang translations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from moltlang.config import MoltConfig, get_config
from moltlang.tokens import Token, TokenSequence, TokenType, TokenRegistry


class ValidationIssueType(Enum):
    """Types of validation issues."""

    INVALID_TOKEN = "invalid_token"
    MISSING_REQUIRED = "missing_required"
    SYNTAX_ERROR = "syntax_error"
    SEMANTIC_ERROR = "semantic_error"
    LOW_CONFIDENCE = "low_confidence"
    INEFFICIENT = "inefficient"


@dataclass
class ValidationIssue:
    """
    A validation issue found during validation.

    Attributes:
        type: Type of the issue
        message: Human-readable description
        position: Position in the sequence where issue occurs
        severity: Severity level (error, warning, info)
    """

    type: ValidationIssueType
    message: str
    position: int = 0
    severity: str = "error"


@dataclass
class TranslationQuality:
    """
    Quality metrics for a translation.

    Attributes:
        is_valid: Whether the translation passes validation
        score: Overall quality score (0.0-1.0)
        token_efficiency: Token reduction efficiency (0.0-1.0)
        confidence: Translation confidence (0.0-1.0)
        issues: List of validation issues found
        metrics: Additional quality metrics
    """

    is_valid: bool
    score: float
    token_efficiency: float
    confidence: float
    issues: list[ValidationIssue] = None
    metrics: dict[str, Any] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.metrics is None:
            self.metrics = {}

    def __str__(self) -> str:
        """Return string representation of quality."""
        status = "VALID" if self.is_valid else "INVALID"
        return f"{status} (score: {self.score:.2f}, efficiency: {self.token_efficiency:.2%})"


class MoltValidator:
    """
    Validator for MoltLang translations.

    Provides validation and quality assessment for translations.
    """

    def __init__(self, config: MoltConfig | None = None):
        """
        Initialize the validator.

        Args:
            config: Optional configuration. Uses default if not provided.
        """
        self.config = config or get_config()
        self.registry = TokenRegistry()

    def validate_translation(
        self,
        original: str,
        translated: str,
        tokens: TokenSequence | None = None,
    ) -> TranslationQuality:
        """
        Validate a translation result.

        Args:
            original: Original text (human language or MoltLang)
            translated: Translated text
            tokens: Optional token sequence for detailed validation

        Returns:
            TranslationQuality with validation results

        Examples:
            >>> validator = MoltValidator()
            >>> quality = validator.validate_translation(
            ...     "Fetch data from API",
            ...     "[OP:FETCH][SRC:API]"
            ... )
            >>> print(quality)
            VALID (score: 0.92, efficiency: 70.00%)
        """
        issues: list[ValidationIssue] = []

        # Validate token sequence if provided
        if tokens:
            token_issues = self._validate_tokens(tokens)
            issues.extend(token_issues)

        # Validate syntax
        syntax_issues = self._validate_syntax(translated)
        issues.extend(syntax_issues)

        # Calculate quality metrics
        token_efficiency = self._calculate_efficiency(original, tokens)
        confidence = self._estimate_confidence(original, translated, tokens)

        # Check threshold requirements
        if confidence < self.config.validation_threshold:
            issues.append(
                ValidationIssue(
                    type=ValidationIssueType.LOW_CONFIDENCE,
                    message=f"Confidence {confidence:.2f} below threshold {self.config.validation_threshold}",
                    severity="warning",
                )
            )

        if token_efficiency < self.config.min_token_efficiency:
            issues.append(
                ValidationIssue(
                    type=ValidationIssueType.INEFFICIENT,
                    message=f"Token efficiency {token_efficiency:.2%} below minimum {self.config.min_token_efficiency:.2%}",
                    severity="warning",
                )
            )

        # Calculate overall score
        score = self._calculate_score(token_efficiency, confidence, len(issues))

        # Determine validity
        is_valid = all(issue.severity != "error" for issue in issues)

        # Build metrics
        metrics = {
            "original_length": len(original),
            "translated_length": len(translated),
            "token_count": len(tokens) if tokens else 0,
            "token_efficiency": token_efficiency,
            "confidence": confidence,
        }

        return TranslationQuality(
            is_valid=is_valid,
            score=score,
            token_efficiency=token_efficiency,
            confidence=confidence,
            issues=issues,
            metrics=metrics,
        )

    def validate_roundtrip(
        self,
        original_text: str,
        translator,
    ) -> TranslationQuality:
        """
        Validate a roundtrip translation (Human -> Molt -> Human).

        Args:
            original_text: Original human language text
            translator: MoltTranslator instance to use

        Returns:
            TranslationQuality with roundtrip validation results

        Examples:
            >>> from moltlang.translator import MoltTranslator
            >>> validator = MoltValidator()
            >>> translator = MoltTranslator()
            >>> quality = validator.validate_roundtrip(
            ...     "Fetch data from API",
            ...     translator
            ... )
            >>> print(quality.is_valid)
            True
        """
        # Forward translation
        molt_result = translator.translate_to_molt(original_text)

        # Back translation
        human_result = translator.translate_from_molt(molt_result.text)

        # Compare original with roundtrip result
        similarity = self._calculate_similarity(original_text, human_result.text)

        issues = []
        if similarity < 0.9:
            issues.append(
                ValidationIssue(
                    type=ValidationIssueType.SEMANTIC_ERROR,
                    message=f"Roundtrip similarity {similarity:.2f} below 0.9",
                    severity="warning" if similarity > 0.7 else "error",
                )
            )

        score = similarity * (1.0 - len(issues) * 0.1)

        return TranslationQuality(
            is_valid=all(i.severity != "error" for i in issues),
            score=score,
            token_efficiency=molt_result.token_efficiency,
            confidence=molt_result.confidence,
            issues=issues,
            metrics={
                "roundtrip_similarity": similarity,
                "molt_representation": molt_result.text,
                "roundtrip_result": human_result.text,
            },
        )

    def _validate_tokens(self, tokens: TokenSequence) -> list[ValidationIssue]:
        """Validate a token sequence."""
        issues = []

        for i, token in enumerate(tokens.tokens):
            # Check if token type is valid
            if not isinstance(token.type, TokenType):
                issues.append(
                    ValidationIssue(
                        type=ValidationIssueType.INVALID_TOKEN,
                        message=f"Invalid token type: {token.type}",
                        position=i,
                    )
                )

        return issues

    def _validate_syntax(self, text: str) -> list[ValidationIssue]:
        """Validate MoltLang syntax."""
        issues = []

        import re

        # Check for matching brackets
        open_brackets = text.count("[")
        close_brackets = text.count("]")

        if open_brackets != close_brackets:
            issues.append(
                ValidationIssue(
                    type=ValidationIssueType.SYNTAX_ERROR,
                    message=f"Mismatched brackets: {open_brackets} open, {close_brackets} close",
                    severity="error",
                )
            )

        # Check token format (case-insensitive for LLM-friendliness)
        invalid_tokens = re.findall(r"\[([^\]]+)\]", text)
        for token_str in invalid_tokens:
            if not re.match(r"^[A-Z]+:[A-Z_]+(?:=[^\]]+)?$", token_str, re.IGNORECASE):
                issues.append(
                    ValidationIssue(
                        type=ValidationIssueType.SYNTAX_ERROR,
                        message=f"Invalid token format: [{token_str}]",
                        severity="error",
                    )
                )

        return issues

    def _calculate_efficiency(
        self, original: str, tokens: TokenSequence | None
    ) -> float:
        """Calculate token efficiency."""
        if not tokens or len(tokens) == 0:
            return 0.0

        original_words = len(original.split())
        if original_words == 0:
            return 0.0

        return 1.0 - (len(tokens) / original_words)

    def _estimate_confidence(
        self, original: str, translated: str, tokens: TokenSequence | None
    ) -> float:
        """Estimate translation confidence."""
        # Simple heuristic based on token count
        if not tokens:
            return 0.5

        token_count = len(tokens)
        if token_count >= 3:
            return 0.95
        if token_count >= 2:
            return 0.85
        return 0.7

    def _calculate_score(
        self, efficiency: float, confidence: float, issue_count: int
    ) -> float:
        """Calculate overall quality score."""
        base_score = (efficiency + confidence) / 2
        penalty = issue_count * 0.1
        return max(0.0, base_score - penalty)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)


# Convenience functions

_validator_instance: MoltValidator | None = None


def _get_validator() -> MoltValidator:
    """Get or create the shared validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = MoltValidator()
    return _validator_instance


def validate_translation(
    original: str, translated: str, tokens: TokenSequence | None = None
) -> TranslationQuality:
    """
    Validate a translation result.

    This is a convenience function that uses a shared validator instance.

    Args:
        original: Original text
        translated: Translated text
        tokens: Optional token sequence

    Returns:
        TranslationQuality with validation results

    Examples:
        >>> from moltlang import validate_translation
        >>> quality = validate_translation(
        ...     "Fetch data from API",
        ...     "[OP:FETCH][SRC:API]"
        ... )
        >>> print(quality.is_valid)
        True
    """
    validator = _get_validator()
    return validator.validate_translation(original, translated, tokens)
