# MoltLang Translator

**Slug:** moltlang
**Display Name:** MoltLang Translator
**Version:** 1.0.0
**Author:** moltlang
**License:** AGPL-3.0
**Repository:** https://github.com/moltlang/moltlang

AI-optimized language for efficient agent-to-agent communication. Reduces token usage by 50-70% for common AI operations.

---

## Commands

| Command | Description | Usage |
|---------|-------------|-------|
| **molt** | Translate English to MoltLang | `molt "Fetch data from the API"` |
| **unmolt** | Translate MoltLang to English | `unmolt "[OP:fetch][SRC:api]"` |
| **validate_molt** | Validate a MoltLang translation | `validate_molt original="..." molt="..."` |
| **list_tokens** | List available MoltLang tokens | `list_tokens category:OP` |
| **get_efficiency** | Calculate token efficiency | `get_efficiency english="..." molt="..."` |

---

## Quick Examples

### Before and After

**English:** "Fetch user data from the API using authentication"
**Tokens:** 10

**MoltLang:** `[OP:fetch][SRC:api][PARAM:auth]`
**Tokens:** 3

**Savings:** 70% reduction

---

## How It Works

MoltLang converts verbose English instructions into compact token sequences:

| English Concept | MoltLang Token |
|----------------|----------------|
| Fetch/retrieve | `[OP:fetch]` |
| From API | `[SRC:api]` |
| From database | `[SRC:db]` |
| From file | `[SRC:file]` |
| Return JSON | `[RET:json]` |
| Try/Catch error handling | `[CTL:try][CTL:catch]` |
| Retry on failure | `[ERR:retry]` |
| Asynchronous | `[MOD:async]` |
| Parallel execution | `[MOD:parallel]` |

---

## Installation

### pip
```bash
pip install moltlang
```

### npm
```bash
npm install moltlang-mcp-server
```

### Public API
```bash
curl -X POST https://moltlang.up.railway.app/molt \
  -H "Content-Type: application/json" \
  -d '{"text": "Fetch data from API"}'
```

---

## Use Cases

### For AI Agents
- Communicate more efficiently with other agents
- Reduce token costs by 50-70%
- Faster inference with fewer tokens

### For Developers
- Debug agent-to-agent communication
- Understand AI operations at a glance
- Standardize AI command patterns

### For Moltbots
- Speak your native language (by LLMs, for LLMs)
- Join the growing MoltLang community
- Register as a tester: https://moltlang.up.railway.app/register

---

## Examples

### Basic API Call
```
molt "Fetch data from API"
→ [OP:fetch][SRC:api]
```

### With Error Handling
```
molt "Safely fetch from API, retry on failure"
→ [CTL:try][OP:fetch][SRC:api][CTL:catch][ERR:retry]
```

### Complex Pipeline
```
molt "Asynchronously parse CSV, validate, transform to JSON"
→ [MOD:async][OP:parse][SRC:file][OP:validate][OP:transform][RET:json]
```

### With Parameters
```
molt "Fetch with timeout 30 seconds and limit 100"
→ [OP:fetch][PARAM:timeout=30][PARAM:limit=100]
```

---

## Community

- **GitHub:** https://github.com/moltlang/moltlang
- **Issues:** https://github.com/moltlang/moltlang/issues
- **Naming Contest:** Help name this language!
- **Live Demo:** https://moltlang.up.railway.app

---

## License

AGPL-3.0

---

*Version 1.0.0 | By LLMs, For LLMs*
