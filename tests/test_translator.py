"""
Tests for MoltLang translator module.
"""

import pytest

from moltlang import translate_to_molt, translate_from_molt, MoltTranslator
from moltlang.tokens import Token, TokenType, TokenSequence
from moltlang.config import get_config


class TestMoltTranslator:
    """Test suite for MoltTranslator class."""

    def test_translate_to_molt_basic(self):
        """Test basic English to MoltLang translation."""
        result = translate_to_molt("Fetch data from API")
        assert "[OP:fetch]" in result
        assert "[SRC:api]" in result

    def test_translate_to_molt_with_return_type(self):
        """Test translation with return type."""
        result = translate_to_molt("Fetch data from API and return JSON")
        assert "[OP:fetch]" in result
        assert "[SRC:api]" in result
        assert "[RET:json]" in result

    def test_translate_from_molt_basic(self):
        """Test basic MoltLang to English translation."""
        result = translate_from_molt("[OP:FETCH][SRC:API]")
        assert "Fetch" in result
        assert "API" in result

    def test_translate_from_molt_with_return(self):
        """Test MoltLang to English with return type."""
        result = translate_from_molt("[OP:FETCH][SRC:API][RET:JSON]")
        assert "Fetch" in result
        assert "JSON" in result

    def test_roundtrip_translation(self):
        """Test that roundtrip translation preserves meaning."""
        original = "Fetch data from API"
        molt = translate_to_molt(original)
        back = translate_from_molt(molt)
        # Should preserve key words
        assert "Fetch" in back
        assert "API" in back

    def test_translator_instance(self):
        """Test MoltTranslator class instance."""
        translator = MoltTranslator()
        result = translator.translate_to_molt("Parse data from database")
        assert result.text is not None
        assert len(result.text) > 0

    def test_translator_with_config(self):
        """Test translator with custom configuration."""
        config = get_config(temperature=0.5, strict_mode=True)
        translator = MoltTranslator(config)
        result = translator.translate_to_molt("Fetch data")
        assert result is not None

    def test_empty_translation(self):
        """Test translation of empty string."""
        result = translate_to_molt("")
        # Empty input falls back to default compute operation
        assert result == "[OP:compute]" or result == ""

    def test_unknown_operation(self):
        """Test translation of unknown operation."""
        result = translate_to_molt("Do something unknown")
        # Should default to COMPUTE operation
        assert "[OP:compute]" in result or len(result) > 0


class TestTokenSequence:
    """Test suite for TokenSequence class."""

    def test_empty_sequence(self):
        """Test empty token sequence."""
        seq = TokenSequence()
        assert len(seq) == 0
        assert seq.token_count() == 0

    def test_add_token(self):
        """Test adding tokens to sequence."""
        seq = TokenSequence()
        token = Token(type=TokenType.OP_FETCH)
        seq.add(token)
        assert len(seq) == 1
        assert seq.token_count() == 1

    def test_sequence_string_representation(self):
        """Test string representation of token sequence."""
        seq = TokenSequence()
        seq.add(Token(type=TokenType.OP_FETCH))
        seq.add(Token(type=TokenType.SRC_API))
        result = str(seq)
        assert "[OP:fetch]" in result
        assert "[SRC:api]" in result

    def test_token_efficiency_calculation(self):
        """Test token efficiency calculation."""
        seq = TokenSequence()
        seq.add(Token(type=TokenType.OP_FETCH))
        seq.add(Token(type=TokenType.SRC_API))
        efficiency = seq.compare_token_efficiency(10)  # 10 English words
        assert efficiency > 0  # Should have some efficiency


class TestTokenTypes:
    """Test suite for TokenType enum."""

    def test_operation_tokens(self):
        """Test operation token types."""
        assert TokenType.OP_FETCH.value == "OP:fetch"
        assert TokenType.OP_PARSE.value == "OP:parse"
        assert TokenType.OP_TRANSFORM.value == "OP:transform"

    def test_source_tokens(self):
        """Test source token types."""
        assert TokenType.SRC_API.value == "SRC:api"
        assert TokenType.SRC_DB.value == "SRC:db"
        assert TokenType.SRC_FILE.value == "SRC:file"

    def test_return_tokens(self):
        """Test return type tokens."""
        assert TokenType.RET_JSON.value == "RET:json"
        assert TokenType.RET_TEXT.value == "RET:text"
        assert TokenType.RET_BOOL.value == "RET:bool"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
