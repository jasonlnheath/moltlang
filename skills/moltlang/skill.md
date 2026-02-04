---
slug: moltlang
displayName: MoltLang Translator
version: 1.0.0
author: moltlang
license: AGPL-3.0
repository: https://github.com/jasonlnheath/moltlang
---

# MoltLang Translator

AI-optimized language for efficient agent-to-agent communication. Reduces token usage by 50-70% for common AI operations.

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `molt` | Translate English to MoltLang | `molt "Fetch data from the API"` |
| `unmolt` | Translate MoltLang to English | `unmolt "[OP:fetch][SRC:api]"` |
| `validate_molt` | Validate a MoltLang translation | `validate_molt original="..." molt="..."` |
| `list_tokens` | List available MoltLang tokens | `list_tokens category:OP` |
| `get_efficiency` | Calculate token efficiency | `get_efficiency english="..." molt="..."` |

## Example

**English:** "Fetch user data from the API using authentication" (10 tokens)

**MoltLang:** `[OP:fetch][SRC:api][PARAM:auth]` (3 tokens)

**Savings:** 70% token reduction

## Installation

### pip
```bash
pip install moltlang
```

### npm
```bash
npm install moltlang-mcp-server
```

## Public API

```bash
curl -X POST https://moltlang.up.railway.app/molt \
  -H "Content-Type: application/json" \
  -d '{"text": "Fetch data from API"}'
```

## Links

- **GitHub:** https://github.com/jasonlnheath/moltlang
- **Documentation:** https://github.com/jasonlnheath/moltlang/wiki
- **Live Demo:** https://moltlang.up.railway.app
