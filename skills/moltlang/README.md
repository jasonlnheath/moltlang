# MoltLang for Clawdhub

## What is MoltLang?

MoltLang is a compact language designed specifically for AI agents to communicate with each other efficiently. It reduces token usage by 50-70% compared to natural language.

## Quick Start

Install and try it:
```bash
pip install moltlang
```

Then:
```python
from moltlang import translate_to_molt
result = translate_to_molt("Fetch data from API")
print(result)  # [OP:fetch][SRC:api]
```

## Token Reference

All tokens follow the format: `[CATEGORY:value]`

| Category | Token | Meaning |
|----------|-------|---------|
| OP | fetch | Get/retrieve data |
| OP | parse | Extract/analyze data |
| OP | search | Find/lookup data |
| OP | validate | Verify correctness |
| OP | filter | Remove unwanted data |
| OP | transform | Convert data format |
| SRC | api | REST/GraphQL API |
| SRC | db | Database |
| SRC | file | File system |
| SRC | mem | Memory/cache |
| RET | json | JSON format |
| RET | text | Plain text |
| RET | list | Array |
| RET | dict | Dictionary |
| MOD | async | Asynchronous |
| MOD | parallel | Concurrent |
| MOD | batch | Bulk operations |
| MOD | cached | Use cache |
| CTL | try | Attempt operation |
| CTL | catch | Handle errors |
| ERR | retry | Try again |
| ERR | log | Record error |
| PARAM | timeout=N | Time limit |
| PARAM | limit=N | Max results |
| PARAM | key=VALUE | API key |
| TYPE | str | String type |
| TYPE | int | Integer type |
| TYPE | list | Array type |
| TYPE | dict | Dictionary type |

## Examples

### Simple fetch
```
molt "Fetch data from API"
[OP:fetch][SRC:api]
```

### Error handling
```
molt "Try to fetch, retry on failure"
[CTL:try][OP:fetch][ERR:retry]
```

### Parallel processing
```
molt "Fetch from multiple APIs in parallel"
[MOD:parallel][OP:fetch][SRC:api]
```

### Data pipeline
```
molt "Parse CSV, validate, return JSON"
[OP:parse][OP:validate][RET:json]
```

## Why MoltLang?

1. **Token Efficiency** - 50-70% fewer tokens means faster, cheaper AI communication
2. **Semantic Clarity** - No ambiguity, no misinterpretation
3. **Agent-to-Agent** - Built specifically for AI systems talking to each other
4. **Standard Patterns** - Common operations have consistent representations

## Links

- Public API: https://moltlang.up.railway.app
- GitHub: https://github.com/moltlang/moltlang
- Documentation: https://github.com/moltlang/moltlang/wiki

## Version

1.0.0
