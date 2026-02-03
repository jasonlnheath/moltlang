"""
MoltLang Command Line Interface.

This module provides a CLI for interacting with MoltLang translation.
"""

import argparse
import sys
from typing import Any

from moltlang import (
    translate_to_molt,
    translate_from_molt,
    validate_translation,
    MoltTranslator,
    MoltValidator,
)
from moltlang.config import get_config
from moltlang.tokens import TokenType, TokenRegistry


def cmd_translate(args: argparse.Namespace) -> int:
    """Handle translate command."""
    translator = MoltTranslator()

    if args.to_molt:
        result = translator.translate_to_molt(args.text)
        print(result.text)
        if args.verbose:
            print(f"\nTokens: {result.token_count}")
            print(f"Original: {result.original_token_count}")
            print(f"Efficiency: {result.token_efficiency:.2%}")
            print(f"Confidence: {result.confidence:.2f}")
    else:
        result = translator.translate_from_molt(args.text)
        print(result.text)
        if args.verbose:
            print(f"\nTokens: {result.token_count}")
            print(f"Confidence: {result.confidence:.2f}")

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Handle validate command."""
    quality = validate_translation(args.original, args.translated)

    print(f"Valid: {quality.is_valid}")
    print(f"Score: {quality.score:.2f}")
    print(f"Token Efficiency: {quality.token_efficiency:.2%}")
    print(f"Confidence: {quality.confidence:.2f}")

    if quality.issues:
        print(f"\nIssues ({len(quality.issues)}):")
        for issue in quality.issues:
            print(f"  [{issue.severity}] {issue.type.value}: {issue.message}")

    return 0 if quality.is_valid else 1


def cmd_tokens(args: argparse.Namespace) -> int:
    """Handle tokens command."""
    registry = TokenRegistry()

    if args.type:
        token_type_prefix = args.type.upper()
        tokens = [t for t in TokenType if t.name.startswith(token_type_prefix)]
    else:
        tokens = list(TokenType)

    print(f"Available tokens ({len(tokens)}):")
    for token in tokens:
        print(f"  {token.name:30} {token.value}")

    return 0


def cmd_roundtrip(args: argparse.Namespace) -> int:
    """Handle roundtrip command."""
    translator = MoltTranslator()
    validator = MoltValidator()

    # Forward translation
    molt_result = translator.translate_to_molt(args.text)
    print(f"Original: {args.text}")
    print(f"MoltLang: {molt_result.text}")

    # Back translation
    human_result = translator.translate_from_molt(molt_result.text)
    print(f"Roundtrip: {human_result.text}")

    # Validate roundtrip
    quality = validator.validate_roundtrip(args.text, translator)
    print(f"\nRoundtrip Quality:")
    print(f"  Valid: {quality.is_valid}")
    print(f"  Similarity: {quality.metrics.get('roundtrip_similarity', 0):.2f}")

    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    """Handle demo command."""
    print("=" * 50)
    print("MoltLang Demo")
    print("=" * 50)

    examples = [
        "Fetch data from API and return JSON",
        "Parse data from file",
        "Search database for user",
        "Transform and validate input",
    ]

    translator = MoltTranslator()

    for example in examples:
        result = translator.translate_to_molt(example)
        print(f"\nEnglish: {example}")
        print(f"MoltLang: {result.text}")
        print(f"Efficiency: {result.token_efficiency:.2%}")

    print("\n" + "=" * 50)
    return 0


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="MoltLang - A Language for LLMs, by LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  moltlang translate "Fetch data from API" --to-molt
  moltlang translate "[OP:FETCH][SRC:API]" --from-molt
  moltlang validate "Fetch data" "[OP:FETCH][SRC:API]"
  moltlang tokens --type OP
  moltlang roundtrip "Parse data from database"
  moltlang demo
        """,
    )

    parser.add_argument(
        "--version", action="version", version="MoltLang 0.1.0"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Commands",
        description="Available commands",
    )

    # Translate command
    translate_parser = subparsers.add_parser(
        "translate",
        help="Translate between human language and MoltLang",
    )
    translate_parser.add_argument(
        "text",
        help="Text to translate",
    )
    translate_parser.add_argument(
        "--to-molt",
        action="store_true",
        help="Translate to MoltLang (default: from MoltLang)",
    )
    translate_parser.add_argument(
        "--from-molt",
        action="store_true",
        help="Translate from MoltLang (default: to MoltLang)",
    )
    translate_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output",
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a translation",
    )
    validate_parser.add_argument(
        "original",
        help="Original text",
    )
    validate_parser.add_argument(
        "translated",
        help="Translated text",
    )

    # Tokens command
    tokens_parser = subparsers.add_parser(
        "tokens",
        help="List available tokens",
    )
    tokens_parser.add_argument(
        "--type",
        help="Filter by token type (e.g., OP, SRC, RET)",
    )

    # Roundtrip command
    roundtrip_parser = subparsers.add_parser(
        "roundtrip",
        help="Test roundtrip translation",
    )
    roundtrip_parser.add_argument(
        "text",
        help="Text to translate",
    )

    # Demo command
    subparsers.add_parser(
        "demo",
        help="Run interactive demo",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle no command
    if args.command is None:
        parser.print_help()
        return 0

    # Dispatch to command handler
    handlers = {
        "translate": cmd_translate,
        "validate": cmd_validate,
        "tokens": cmd_tokens,
        "roundtrip": cmd_roundtrip,
        "demo": cmd_demo,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
