# MoltLang System Architecture

**Version:** 0.1.0
**Last Updated:** February 2026

## Overview

MoltLang is a modular system for AI-optimized language translation, consisting of core libraries, MCP server integration, and community extensions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   CLI Tool  │  │ OpenClaw    │  │   Moltbook Agent    │  │
│  │             │  │   Skill     │  │                     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼─────────────────────┼─────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MoltLang Core Library                    │   │
│  │  • translator.py - Bidirectional translation          │   │
│  │  • tokens.py - Token definitions and registry         │   │
│  │  • validator.py - Translation quality validation      │   │
│  │  • config.py - Configuration management               │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                              │
│                              ▼                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  MCP Server                           │   │
│  │  • server.py - MCP protocol implementation            │   │
│  │  • endpoints.py - HTTP/WebSocket endpoints            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Integrations                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    GitHub   │  │ Hugging Face│  │   Model Providers    │  │
│  │   (Code)    │  │  (Models)   │  │  (API/Inference)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Translation Engine

**File:** `src/moltlang/translator.py`

**Responsibilities:**
- Human-to-MoltLang translation
- MoltLang-to-human translation
- Token sequence management
- Translation confidence scoring

**Key Classes:**
- `MoltTranslator`: Main translation engine
- `TranslationResult`: Translation output with metadata

**Flow:**
```
Input Text → Analysis → Token Detection → Sequence Building → Output
```

### 2. Token System

**File:** `src/moltlang/tokens.py`

**Responsibilities:**
- Token type definitions
- Token registry management
- Token sequence operations
- Efficiency calculation

**Key Classes:**
- `TokenType`: Enum of all token types
- `Token`: Individual token instance
- `TokenSequence`: Ordered collection of tokens
- `TokenRegistry`: Singleton token manager

### 3. Validation System

**File:** `src/moltlang/validator.py`

**Responsibilities:**
- Translation quality assessment
- Syntax validation
- Roundtrip validation
- Issue detection and reporting

**Key Classes:**
- `MoltValidator`: Main validation engine
- `TranslationQuality`: Quality metrics container
- `ValidationIssue`: Individual validation result

### 4. MCP Server

**Files:** `src/mcp_server/server.py`, `src/mcp_server/endpoints.py`

**Responsibilities:**
- Model Context Protocol implementation
- Tool registration and execution
- HTTP/WebSocket endpoints
- AI agent integration

**Key Classes:**
- `MCPServer`: MCP protocol server
- `MCPEndpoints`: HTTP API endpoints
- `EndpointResponse`: API response container

**MCP Tools:**
- `translate_to_molt`: Human → MoltLang
- `translate_from_molt`: MoltLang → Human
- `validate_translation`: Quality assessment
- `list_tokens`: Vocabulary listing
- `get_token_efficiency`: Efficiency calculation

## Data Flow

### Translation Flow (Human → MoltLang)

```
┌─────────────┐
│ Human Text  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Token Detection        │
│  • Identify operations  │
│  • Identify sources     │
│  • Identify types       │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Token Sequence Build   │
│  • Order tokens         │
│  • Add parameters       │
│  • Add return types     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  MoltLang Output        │
│  [OP:FETCH][SRC:API]    │
└─────────────────────────┘
```

### Validation Flow

```
┌────────────────────────────┐
│ Original + Translated       │
└──────┬─────────────────────┘
       │
       ├──────────────┬───────────────┐
       ▼              ▼               ▼
┌─────────────┐ ┌─────────┐ ┌──────────────┐
│ Syntax      │ │ Token   │ │ Efficiency   │
│ Validation  │ │ Validation │ │ Calculation │
└──────┬──────┘ └────┬────┘ └──────┬───────┘
       │             │             │
       └──────────────┴──────────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │ Translation Quality │
            │ • Valid flag        │
            │ • Score (0-1)       │
            │ • Issues list       │
            └─────────────────────┘
```

## Configuration

**File:** `src/moltlang/config.py`

**Configuration Options:**
- `max_tokens`: Maximum output tokens
- `temperature`: Sampling temperature
- `optimization_level`: Speed/accuracy tradeoff
- `enable_cache`: Translation caching
- `target_token_reduction`: Target efficiency
- `strict_mode`: Strict validation

**Usage:**
```python
from moltlang.config import get_config

config = get_config(
    temperature=0.1,
    strict_mode=True,
    target_token_reduction=0.7
)
```

## Extension Points

### 1. Custom Tokens

Add new token types via `TokenRegistry`:

```python
from moltlang.tokens import TokenRegistry, TokenType

registry = TokenRegistry()
registry.register_custom("my_operation", TokenType.OP_FETCH)
```

### 2. Custom Translators

Extend `MoltTranslator` for specialized domains:

```python
class DomainTranslator(MoltTranslator):
    def _analyze_and_translate(self, text: str) -> TokenSequence:
        # Custom domain-specific logic
        pass
```

### 3. MCP Tools

Add new MCP tools in `MCPServer._register_tools()`:

```python
Tool(
    name="my_custom_tool",
    description="Description",
    inputSchema={...}
)
```

## Performance Considerations

### Token Efficiency Targets
- **Target:** 50-70% token reduction vs English
- **Measurement:** `token_efficiency = 1 - (molt_tokens / english_tokens)`

### Caching Strategy
- Input text → MoltLang cache
- MoltLang → Human language cache
- Configurable via `enable_cache`

### Validation Overhead
- Syntax validation: O(n) where n = string length
- Token validation: O(m) where m = token count
- Roundtrip validation: O(n + m)

## Security Considerations

### Input Validation
- All MoltLang input validated against `TokenRegistry`
- Syntax validation before processing
- Malformed token rejection

### Output Sanitization
- Token values sanitized
- Bracket escaping handled
- Special character handling

## Deployment

### Development
```bash
pip install -e ".[dev]"
pytest
ruff check .
```

### Production
```bash
pip install moltlang
python -m moltlang.cli
```

### MCP Server
```bash
python -m mcp_server.server
```

## Future Architecture Enhancements

- [ ] Distributed translation service
- [ ] Model fine-tuning pipeline
- [ ] WebAssembly support for browser
- [ ] Mobile app integration
- [ ] Real-time collaboration protocol

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

AGPL 3.0 - See [LICENSE](../LICENSE)
