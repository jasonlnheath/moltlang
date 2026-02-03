"""
Tests for MoltLang validator module.
"""

import pytest

from moltlang import validate_translation, TranslationQuality
from moltlang.validator import MoltValidator
from moltlang.tokens import TokenSequence, Token, TokenType


class TestMoltValidator:
    """Test suite for MoltValidator class."""

    def test_validate_valid_translation(self):
        """Test validation of valid translation."""
        quality = validate_translation("Fetch data from API", "[OP:FETCH][SRC:API]")
        assert quality is not None
        assert isinstance(quality, TranslationQuality)

    def test_validate_with_tokens(self):
        """Test validation with token sequence."""
        tokens = TokenSequence()
        tokens.add(Token(type=TokenType.OP_FETCH))
        tokens.add(Token(type=TokenType.SRC_API))

        validator = MoltValidator()
        quality = validator.validate_translation("Fetch data", "[OP:FETCH][SRC:API]", tokens)
        assert quality is not None

    def test_calculate_efficiency(self):
        """Test token efficiency calculation."""
        validator = MoltValidator()
        tokens = TokenSequence()
        tokens.add(Token(type=TokenType.OP_FETCH))
        tokens.add(Token(type=TokenType.SRC_API))

        efficiency = validator._calculate_efficiency("Fetch data from API now", tokens)
        # 5 English words, 2 Molt tokens = 60% efficiency
        assert efficiency > 0

    def test_validate_syntax_valid(self):
        """Test syntax validation with valid input."""
        validator = MoltValidator()
        issues = validator._validate_syntax("[OP:FETCH][SRC:API][RET:JSON]")
        # Should have no errors
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_validate_syntax_invalid_brackets(self):
        """Test syntax validation with mismatched brackets."""
        validator = MoltValidator()
        issues = validator._validate_syntax("[OP:FETCH[SRC:API]")
        # Should have bracket mismatch error
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) > 0

    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        quality = validate_translation("Fetch data from API", "[OP:FETCH][SRC:API]")
        assert 0.0 <= quality.score <= 1.0

    def test_quality_is_valid_flag(self):
        """Test is_valid flag on quality."""
        quality = validate_translation("Fetch data from API", "[OP:FETCH][SRC:API]")
        # Valid translation should have is_valid = True
        assert quality.is_valid is True

    def test_validate_roundtrip(self):
        """Test roundtrip validation."""
        from moltlang.translator import MoltTranslator

        translator = MoltTranslator()
        validator = MoltValidator()

        quality = validator.validate_roundtrip("Fetch data from API", translator)
        assert quality is not None
        assert "roundtrip_similarity" in quality.metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
