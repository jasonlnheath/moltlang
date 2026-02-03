# MoltLang Tutorial

**Version:** 0.1.0
**Last Updated:** February 2026

Welcome to MoltLang! This tutorial will guide you through the basics of using MoltLang for AI-optimized communication.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Translation](#basic-translation)
4. [Understanding Tokens](#understanding-tokens)
5. [Building Token Sequences](#building-token-sequences)
6. [Validation](#validation)
7. [Advanced Configuration](#advanced-configuration)
8. [MCP Integration](#mcp-integration)
9. [OpenClaw Integration](#openclaw-integration)

---

## Installation

### From Source

```bash
git clone https://github.com/moltlang/moltlang.git
cd moltlang
pip install -e .
```

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

### With MCP Support

```bash
pip install -e ".[mcp]"
```

### Verify Installation

```bash
python -c "from moltlang import translate_to_molt; print('MoltLang installed!')"
moltlang --version
```

---

## Quick Start

### Your First Translation

```python
from moltlang import translate_to_molt, translate_from_molt

# Translate English to MoltLang
molt = translate_to_molt("Fetch data from API and return JSON")
print(molt)  # [OP:FETCH][SRC:API][RET:JSON]

# Translate back to English
english = translate_from_molt(molt)
print(english)  # Fetch data from API return JSON
```

### Using the CLI

```bash
# Translate to MoltLang
moltlang translate "Fetch data from API" --to-molt

# Translate from MoltLang
moltlang translate "[OP:FETCH][SRC:API]" --from-molt

# Validate a translation
moltlang validate "Fetch data" "[OP:FETCH][SRC:API]"
```

---

## Basic Translation

### Understanding Token Efficiency

MoltLang's primary benefit is token efficiency:

```python
from moltlang import translate_to_molt

english = "Fetch data from the API using the provided token and return JSON"
molt = translate_to_molt(english)

# Count tokens
english_tokens = len(english.split())  # ~17 tokens
molt_tokens = molt.count("[")  # 4 tokens

efficiency = 1 - (molt_tokens / english_tokens)
print(f"Efficiency: {efficiency:.1%}")  # ~76% reduction
```

### Common Patterns

| Operation | English | MoltLang | Tokens Saved |
|-----------|---------|----------|--------------|
| API Fetch | "Fetch data from API" | `[OP:FETCH][SRC:API]` | 75% |
| Data Parse | "Parse JSON from file" | `[OP:PARSE][SRC:FILE][RET:JSON]` | 70% |
| Database Query | "Search database for user" | `[OP:SEARCH][SRC:DB]` | 67% |
| Data Transform | "Transform to JSON" | `[OP:TRANSFORM][RET:JSON]` | 60% |

---

## Understanding Tokens

### Token Categories

```python
from moltlang import TokenType

# Operations (actions)
print(TokenType.OP_FETCH)   # OP:FETCH
print(TokenType.OP_PARSE)    # OP:PARSE
print(TokenType.OP_SEARCH)   # OP:SEARCH

# Sources (data sources)
print(TokenType.SRC_API)     # SRC:API
print(TokenType.SRC_DB)      # SRC:DB
print(TokenType.SRC_FILE)    # SRC:FILE

# Return types (output format)
print(TokenType.RET_JSON)    # RET:json
print(TokenType.RET_TEXT)    # RET:text
print(TokenType.RET_BOOL)    # RET:bool
```

### Token Structure

```
[CATEGORY:TYPE=VALUE]
```

- **CATEGORY**: Token category (OP, SRC, RET, etc.)
- **TYPE**: Specific type within category
- **VALUE**: Optional parameter value

Examples:
```
[OP:FETCH]              # Simple token
[PARAM:token=abc123]    # Token with value
[RET:JSON]              # Return type token
```

---

## Building Token Sequences

### Manual Token Building

```python
from moltlang import TokenSequence, Token, TokenType

# Create a sequence
seq = TokenSequence()
seq.add(Token(type=TokenType.OP_FETCH))
seq.add(Token(type=TokenType.SRC_API))
seq.add(Token(type=TokenType.RET_JSON))

print(seq)  # [OP:FETCH][SRC:API][RET:JSON]
print(len(seq))  # 3
```

### Using Convenience Functions

```python
from moltlang.tokens import op, src, ret, sequence

# Build sequence with helpers
seq = sequence(
    op("FETCH"),
    src("API"),
    ret("JSON")
)

print(seq)  # [OP:FETCH][SRC:API][RET:JSON]
```

### Token with Values

```python
from moltlang import Token, TokenType, TokenSequence

# Token with parameter value
token = Token(type=TokenType.PARAM_TOKEN, value="abc123")
print(token)  # [PARAM:token=abc123]

# Add to sequence
seq = TokenSequence()
seq.add(Token(type=TokenType.OP_FETCH))
seq.add(token)
print(seq)  # [OP:FETCH][PARAM:token=abc123]
```

---

## Validation

### Basic Validation

```python
from moltlang import validate_translation

quality = validate_translation(
    "Fetch data from API",
    "[OP:FETCH][SRC:API]"
)

print(f"Valid: {quality.is_valid}")  # True
print(f"Score: {quality.score:.2f}")  # 0.92
print(f"Efficiency: {quality.token_efficiency:.2%}")  # 70.00%
```

### Handling Validation Issues

```python
quality = validate_translation(
    "Fetch data",
    "[OP:FETCH[SRC:API]"  # Invalid: missing closing bracket
)

if not quality.is_valid:
    print(f"Validation failed with {len(quality.issues)} issues:")
    for issue in quality.issues:
        print(f"  - [{issue.severity}] {issue.message}")
```

### Roundtrip Validation

```python
from moltlang import MoltTranslator, MoltValidator

translator = MoltTranslator()
validator = MoltValidator()

# Test roundtrip quality
quality = validator.validate_roundtrip(
    "Fetch data from API",
    translator
)

print(f"Roundtrip similarity: {quality.metrics['roundtrip_similarity']:.2f}")
print(f"Quality score: {quality.score:.2f}")
```

---

## Advanced Configuration

### Custom Configuration

```python
from moltlang.config import get_config, OptimizationLevel
from moltlang import MoltTranslator

# Create custom config
config = get_config(
    temperature=0.1,          # Lower temperature for deterministic output
    target_token_reduction=0.7,  # Target 70% reduction
    strict_mode=True,         # Enable strict validation
    optimization_level=OptimizationLevel.ACCURATE
)

# Use with translator
translator = MoltTranslator(config)
result = translator.translate_to_molt("Fetch data")
print(result.text)
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_tokens` | int | 4096 | Maximum tokens to generate |
| `temperature` | float | 0.3 | Sampling temperature (0.0-1.0) |
| `optimization_level` | OptimizationLevel | BALANCED | Speed/accuracy tradeoff |
| `enable_cache` | bool | True | Enable translation caching |
| `target_token_reduction` | float | 0.6 | Target token reduction (0.0-1.0) |
| `strict_mode` | bool | False | Enable strict validation |
| `human_language` | str | "en" | Target human language |

---

## MCP Integration

### Setting Up MCP Server

```bash
# Install MCP dependencies
pip install -e ".[mcp]"

# Start MCP server
python -m mcp_server.server
```

### Using MCP Endpoints

```python
import asyncio
from mcp_server.endpoints import MCPEndpoints

async def translate_example():
    endpoints = MCPEndpoints()

    # Translate to MoltLang
    response = await endpoints.translate(
        "Fetch data from API",
        to_molt=True
    )
    print(response.data['moltlang'])
    print(f"Efficiency: {response.data['efficiency']:.2%}")

    # Validate translation
    validation = await endpoints.validate(
        "Fetch data",
        "[OP:FETCH]"
    )
    print(f"Valid: {validation.data['is_valid']}")

asyncio.run(translate_example())
```

### Listing Available Tokens

```python
async def list_tokens():
    endpoints = MCPEndpoints()

    # List all tokens
    all_tokens = await endpoints.vocabulary()
    print(f"Total tokens: {all_tokens.data['count']}")

    # List only operations
    op_tokens = await endpoints.vocabulary(token_type="OP")
    print(f"Operations: {op_tokens.data['count']}")

asyncio.run(list_tokens())
```

---

## OpenClaw Integration

### Creating an OpenClaw Skill

```python
from moltlang.openclaw import MoltLangOpenClawSkill

# Create skill instance
skill = MoltLangOpenClawSkill()

# Handle human message
molt = await skill.handle_message(
    "Fetch user data from database",
    context={}
)
print(molt)  # [OP:FETCH][SRC:DB]

# Handle MoltLang message
human = await skill.handle_molt_message(
    "[OP:FETCH][SRC:API][RET:JSON]",
    context={}
)
print(human)  # Fetch data from API return JSON

# Get available commands
commands = skill.get_commands()
for cmd in commands:
    print(f"{cmd['name']}: {cmd['description']}")
```

---

## Next Steps

1. **Explore Examples**: Check out `examples/basic_usage.py` for more examples
2. **Read the Spec**: See `docs/SPEC.md` for the full language specification
3. **Join the Community**: Participate in the naming contest on GitHub Issues
4. **Contribute**: See `CONTRIBUTING.md` for contribution guidelines

## Getting Help

- **Documentation**: `docs/` directory
- **Issues**: https://github.com/moltlang/moltlang/issues
- **Discussions**: https://github.com/moltlang/moltlang/discussions

---

Happy translating! 🤖🔄🤖
