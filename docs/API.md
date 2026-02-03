# MoltLang API Reference

**Version:** 0.1.0
**Last Updated:** February 2026

## Table of Contents

- [Core API](#core-api)
- [Token API](#token-api)
- [Configuration API](#configuration-api)
- [Validation API](#validation-api)
- [MCP API](#mcp-api)
- [CLI API](#cli-api)

---

## Core API

### `translate_to_molt(text: str, config: MoltConfig | None = None) -> str`

Translate human language text to MoltLang.

**Parameters:**
- `text` (str): Human language text to translate
- `config` (MoltConfig | None): Optional configuration override

**Returns:**
- str: MoltLang string representation

**Example:**
```python
from moltlang import translate_to_molt

molt = translate_to_molt("Fetch data from API and return JSON")
print(molt)  # [OP:FETCH][SRC:API][RET:JSON]
```

---

### `translate_from_molt(molt_text: str, config: MoltConfig | None = None) -> str`

Translate MoltLang to human language text.

**Parameters:**
- `molt_text` (str): MoltLang text to translate
- `config` (MoltConfig | None): Optional configuration override

**Returns:**
- str: Human language translation

**Example:**
```python
from moltlang import translate_from_molt

english = translate_from_molt("[OP:FETCH][SRC:API][RET:JSON]")
print(english)  # Fetch data from API return JSON
```

---

### `validate_translation(original: str, translated: str, tokens: TokenSequence | None = None) -> TranslationQuality`

Validate a translation result and return quality metrics.

**Parameters:**
- `original` (str): Original text
- `translated` (str): Translated text
- `tokens` (TokenSequence | None): Optional token sequence for detailed validation

**Returns:**
- TranslationQuality: Quality metrics container

**Example:**
```python
from moltlang import validate_translation

quality = validate_translation(
    "Fetch data from API",
    "[OP:FETCH][SRC:API]"
)
print(quality.is_valid)  # True
print(quality.score)     # 0.92
print(quality.token_efficiency)  # 0.70
```

---

## Token API

### `Token`

Dataclass representing a single MoltLang token.

**Attributes:**
- `type` (TokenType): The token type
- `value` (str | None): Optional value associated with the token
- `position` (int): Position in the token sequence

**Example:**
```python
from moltlang import Token, TokenType

token = Token(type=TokenType.OP_FETCH, value="data")
print(str(token))  # [OP:FETCH=data]
```

---

### `TokenType`

Enum of all available token types.

**Categories:**
- `OP_*`: Operation tokens (FETCH, PARSE, TRANSFORM, etc.)
- `SRC_*`: Source tokens (API, DB, FILE, etc.)
- `PARAM_*`: Parameter tokens (token, key, query, etc.)
- `RET_*`: Return type tokens (json, text, bool, etc.)
- `CTL_*`: Control flow tokens (IF, ELSE, LOOP, etc.)
- `TYPE_*`: Data type tokens (str, int, bool, etc.)
- `ERR_*`: Error handling tokens (RETRY, FAIL, LOG, etc.)
- `MOD_*`: Modifier tokens (ASYNC, BATCH, PARALLEL, etc.)

**Example:**
```python
from moltlang import TokenType

print(TokenType.OP_FETCH.value)  # OP:FETCH
print(TokenType.SRC_API.value)   # SRC:API
```

---

### `TokenSequence`

Dataclass representing a sequence of MoltLang tokens.

**Methods:**
- `add(token: Token) -> TokenSequence`: Add a token to the sequence
- `token_count() -> int`: Return the total token count
- `compare_token_efficiency(english_word_count: int) -> float`: Calculate efficiency

**Example:**
```python
from moltlang import TokenSequence, Token, TokenType

seq = TokenSequence()
seq.add(Token(type=TokenType.OP_FETCH))
seq.add(Token(type=TokenType.SRC_API))
print(str(seq))  # [OP:FETCH][SRC:API]
print(seq.token_count())  # 2
```

---

### `TokenRegistry`

Singleton registry for managing MoltLang tokens.

**Methods:**
- `get(token_str: str) -> Token | None`: Get a token by string representation
- `register_custom(name: str, token_type: TokenType) -> Token`: Register a custom token
- `list_tokens(token_type: TokenType | None = None) -> list[Token]`: List tokens
- `validate_sequence(sequence: TokenSequence) -> bool`: Validate a token sequence

**Example:**
```python
from moltlang import TokenRegistry

registry = TokenRegistry()
token = registry.get("[OP:FETCH]")
print(token.type)  # TokenType.OP_FETCH
```

---

## Configuration API

### `MoltConfig`

Dataclass for MoltLang configuration.

**Attributes:**
- `max_tokens` (int): Maximum tokens to generate (default: 4096)
- `temperature` (float): Sampling temperature 0.0-1.0 (default: 0.3)
- `optimization_level` (OptimizationLevel): Speed/accuracy tradeoff
- `enable_cache` (bool): Enable translation caching (default: True)
- `target_token_reduction` (float): Target reduction 0.0-1.0 (default: 0.6)
- `strict_mode` (bool): Enable strict validation (default: False)
- `human_language` (str): Target human language (default: "en")

**Example:**
```python
from moltlang.config import MoltConfig

config = MoltConfig(
    temperature=0.1,
    strict_mode=True,
    target_token_reduction=0.7
)
```

---

### `get_config(**kwargs) -> MoltConfig`

Get a MoltConfig instance with optional overrides.

**Parameters:**
- `**kwargs`: Configuration overrides

**Returns:**
- MoltConfig: Configured instance

**Example:**
```python
from moltlang.config import get_config

config = get_config(temperature=0.5, strict_mode=True)
print(config.temperature)  # 0.5
```

---

### `OptimizationLevel`

Enum for translation optimization levels.

**Values:**
- `FAST`: Fast translation, lower accuracy
- `BALANCED`: Balance between speed and accuracy
- `ACCURATE`: Highest accuracy, slower

---

## Validation API

### `TranslationQuality`

Dataclass containing translation quality metrics.

**Attributes:**
- `is_valid` (bool): Whether translation passes validation
- `score` (float): Overall quality score (0.0-1.0)
- `token_efficiency` (float): Token reduction efficiency (0.0-1.0)
- `confidence` (float): Translation confidence (0.0-1.0)
- `issues` (list[ValidationIssue]): List of validation issues
- `metrics` (dict[str, Any]): Additional quality metrics

**Example:**
```python
from moltlang import validate_translation

quality = validate_translation("Fetch data", "[OP:FETCH]")
print(quality.is_valid)  # True
print(quality.score)     # 0.92
print(quality.token_efficiency)  # 0.70
for issue in quality.issues:
    print(f"{issue.type}: {issue.message}")
```

---

### `ValidationIssueType`

Enum of validation issue types.

**Values:**
- `INVALID_TOKEN`: Unknown or invalid token
- `MISSING_REQUIRED`: Missing required token
- `SYNTAX_ERROR`: Syntax error in MoltLang
- `SEMANTIC_ERROR`: Semantic meaning error
- `LOW_CONFIDENCE`: Translation confidence below threshold
- `INEFFICIENT`: Token efficiency below minimum

---

### `MoltValidator`

Validator for MoltLang translations.

**Methods:**
- `validate_translation(original: str, translated: str, tokens: TokenSequence | None = None) -> TranslationQuality`
- `validate_roundtrip(original_text: str, translator: MoltTranslator) -> TranslationQuality`

**Example:**
```python
from moltlang import MoltValidator, MoltTranslator

validator = MoltValidator()
translator = MoltTranslator()

quality = validator.validate_roundtrip(
    "Fetch data from API",
    translator
)
print(quality.is_valid)  # True
```

---

## MCP API

### MCPServer

Model Context Protocol server for MoltLang.

**Methods:**
- `call_tool(request: CallToolRequest) -> CallToolResult`: Handle tool call
- `list_tools(request: ListToolsRequest) -> ListToolsResult`: List available tools

**MCP Tools:**
- `translate_to_molt`: Translate human text to MoltLang
- `translate_from_molt`: Translate MoltLang to human text
- `validate_translation`: Validate a translation
- `list_tokens`: List available tokens
- `get_token_efficiency`: Calculate token efficiency

**Example:**
```python
from mcp_server import MCPServer

server = MCPServer()
tools = await server.list_tools(ListToolsRequest())
for tool in tools.tools:
    print(f"{tool.name}: {tool.description}")
```

---

### MCPEndpoints

HTTP/WebSocket endpoints for MoltLang.

**Methods:**
- `translate(text: str, to_molt: bool, target_language: str) -> EndpointResponse`: Translate text
- `validate(original: str, translated: str) -> EndpointResponse`: Validate translation
- `vocabulary(token_type: str | None) -> EndpointResponse`: List vocabulary
- `health() -> EndpointResponse`: Health check

**Example:**
```python
from mcp_server.endpoints import MCPEndpoints

endpoints = MCPEndpoints()
response = await endpoints.translate(
    "Fetch data from API",
    to_molt=True
)
print(response.data['moltlang'])  # [OP:FETCH][SRC:API]
```

---

## CLI API

### Command: `translate`

Translate between human language and MoltLang.

```bash
moltlang translate "Fetch data from API" --to-molt
moltlang translate "[OP:FETCH][SRC:API]" --from-molt
moltlang translate "Fetch data" -v  # verbose output
```

### Command: `validate`

Validate a translation.

```bash
moltlang validate "Fetch data" "[OP:FETCH][SRC:API]"
```

### Command: `tokens`

List available tokens.

```bash
moltlang tokens
moltlang tokens --type OP
moltlang tokens --type SRC
```

### Command: `roundtrip`

Test roundtrip translation.

```bash
moltlang roundtrip "Parse data from database"
```

### Command: `demo`

Run interactive demo.

```bash
moltlang demo
```

---

## Type Aliases

```python
# Token type hints
TokenOrStr = Token | str
TokenList = list[Token]
TranslationDict = dict[str, str | float]
```

---

## Constants

```python
# Version
__version__ = "0.1.0"

# Default configuration
DEFAULT_CONFIG = MoltConfig()

# Validation thresholds
DEFAULT_VALIDATION_THRESHOLD = 0.95
DEFAULT_TOKEN_EFFICIENCY = 0.5
```

---

## Error Handling

### `MoltLangError`

Base exception for MoltLang errors.

### `TranslationError`

Raised when translation fails.

### `ValidationError`

Raised when validation fails (in strict mode).

### `TokenError`

Raised for token-related errors.

---

## See Also

- [Language Specification](SPEC.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Tutorial](TUTORIAL.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
