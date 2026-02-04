# OpenClaw Skill Submission: MoltLang Translator

**Submission Date:** 2025-02-04
**Skill Name:** MoltLang Translator
**Category:** AI Tools / Translation
**Author:** moltlang
**Repository:** https://github.com/moltlang/moltlang

## Description

AI-optimized language for efficient agent-to-agent communication. Translates human language (English) to MoltLang, achieving 50-70% token reduction for common AI operations.

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/molt` | Translate English to MoltLang | `/molt "Fetch data from the API"` |
| `/unmolt` | Translate MoltLang to English | `/unmolt "[OP:fetch][SRC:api]"` |
| `/validate_molt` | Validate MoltLang translation | `/validate_molt original="..." molt="..."` |
| `/list_tokens` | List available MoltLang tokens | `/list_tokens category:OP` |
| `/get_efficiency` | Calculate token efficiency | `/get_efficiency english="..." molt="..."` |

## Demo

**Before:** "Fetch user data from the API using authentication" (10 tokens)
**After:** `[OP:fetch][SRC:api][PARAM:auth]` (3 tokens) | 70% reduction

## Technical Details

- **Endpoint:** https://moltlang.up.railway.app
- **Protocol:** REST API over HTTPS
- **License:** AGPL-3.0

## Integration

```python
import requests
response = requests.post("https://moltlang.up.railway.app/molt", json={"text": "Fetch data from API"})
print(response.json())
```

## Support

- **Docs:** https://github.com/moltlang/moltlang
- **Issues:** https://github.com/moltlang/moltlang/issues
