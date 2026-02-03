"""
MoltLang Basic Usage Examples.

This file demonstrates how to use MoltLang for translation between
human languages and the AI-optimized MoltLang.
"""

from moltlang import (
    translate_to_molt,
    translate_from_molt,
    validate_translation,
    MoltTranslator,
    MoltValidator,
)
from moltlang.tokens import Token, TokenType, TokenSequence, op, src, ret, sequence


def example_basic_translation():
    """Example: Basic English to MoltLang translation."""
    print("=" * 50)
    print("Example 1: Basic Translation")
    print("=" * 50)

    english = "Fetch data from API and return JSON"
    molt = translate_to_molt(english)

    print(f"English: {english}")
    print(f"MoltLang: {molt}")
    print()


def example_reverse_translation():
    """Example: MoltLang to English translation."""
    print("=" * 50)
    print("Example 2: Reverse Translation")
    print("=" * 50)

    molt = "[OP:FETCH][SRC:API][RET:JSON]"
    english = translate_from_molt(molt)

    print(f"MoltLang: {molt}")
    print(f"English: {english}")
    print()


def example_roundtrip_translation():
    """Example: Roundtrip translation with validation."""
    print("=" * 50)
    print("Example 3: Roundtrip with Validation")
    print("=" * 50)

    original = "Parse data from database and return list"
    molt = translate_to_molt(original)
    back = translate_from_molt(molt)

    print(f"Original: {original}")
    print(f"MoltLang: {molt}")
    print(f"Roundtrip: {back}")
    print()

    # Validate the translation
    quality = validate_translation(original, molt)
    print(f"Valid: {quality.is_valid}")
    print(f"Score: {quality.score:.2f}")
    print(f"Token Efficiency: {quality.token_efficiency:.2%}")
    print()


def example_translator_instance():
    """Example: Using translator instance directly."""
    print("=" * 50)
    print("Example 4: Using Translator Instance")
    print("=" * 50)

    translator = MoltTranslator()
    result = translator.translate_to_molt("Search in file and return text")

    print(f"English: Search in file and return text")
    print(f"MoltLang: {result.text}")
    print(f"Token Count: {result.token_count}")
    print(f"Original Tokens: {result.original_token_count}")
    print(f"Efficiency: {result.token_efficiency:.2%}")
    print(f"Confidence: {result.confidence:.2f}")
    print()


def example_token_sequence_building():
    """Example: Building token sequences manually."""
    print("=" * 50)
    print("Example 5: Manual Token Sequence Building")
    print("=" * 50)

    # Build a sequence manually
    seq = TokenSequence()
    seq.add(Token(type=TokenType.OP_FETCH))
    seq.add(Token(type=TokenType.SRC_API))
    seq.add(Token(type=TokenType.RET_JSON))

    print(f"Manual Sequence: {str(seq)}")
    print(f"Token Count: {seq.token_count()}")
    print()

    # Using convenience functions
    seq2 = sequence(op("FETCH"), src("API"), ret("JSON"))
    print(f"Convenience Sequence: {str(seq2)}")
    print()


def example_multiple_translations():
    """Example: Multiple translations for comparison."""
    print("=" * 50)
    print("Example 6: Multiple Translations Comparison")
    print("=" * 50)

    examples = [
        "Fetch data from API",
        "Parse data from file",
        "Transform data and return JSON",
        "Validate input from database",
        "Search for data in memory",
    ]

    for example in examples:
        molt = translate_to_molt(example)
        english_tokens = len(example.split())
        molt_tokens = molt.count("[")
        efficiency = 1.0 - (molt_tokens / english_tokens) if english_tokens > 0 else 0

        print(f"English: {example}")
        print(f"MoltLang: {molt}")
        print(f"Efficiency: {efficiency:.2%} ({english_tokens} → {molt_tokens} tokens)")
        print()


def example_validation_with_issues():
    """Example: Validation showing issues."""
    print("=" * 50)
    print("Example 7: Validation with Issues")
    print("=" * 50)

    # Valid translation
    quality1 = validate_translation("Fetch data", "[OP:FETCH][SRC:API]")
    print("Valid Translation:")
    print(f"  Valid: {quality1.is_valid}")
    print(f"  Score: {quality1.score:.2f}")
    print()

    # Invalid syntax (mismatched brackets)
    quality2 = validate_translation("Fetch data", "[OP:FETCH[SRC:API]")
    print("Invalid Syntax:")
    print(f"  Valid: {quality2.is_valid}")
    print(f"  Issues: {len(quality2.issues)}")
    for issue in quality2.issues:
        print(f"    - {issue.type.value}: {issue.message}")
    print()


def example_custom_configuration():
    """Example: Using custom configuration."""
    print("=" * 50)
    print("Example 8: Custom Configuration")
    print("=" * 50)

    from moltlang.config import get_config

    # Create custom config
    config = get_config(
        temperature=0.1,
        target_token_reduction=0.7,
        strict_mode=True,
        enable_cache=False,
    )

    translator = MoltTranslator(config)
    result = translator.translate_to_molt("Compute results")

    print(f"Translation: {result.text}")
    print(f"Config: temp={config.temperature}, strict={config.strict_mode}")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 50)
    print("MoltLang Basic Usage Examples")
    print("=" * 50 + "\n")

    example_basic_translation()
    example_reverse_translation()
    example_roundtrip_translation()
    example_translator_instance()
    example_token_sequence_building()
    example_multiple_translations()
    example_validation_with_issues()
    example_custom_configuration()

    print("=" * 50)
    print("All examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
