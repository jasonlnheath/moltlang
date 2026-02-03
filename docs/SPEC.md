# MoltLang Language Specification v0.1

**Status:** Draft - Community Input Welcome
**Version:** 0.1.0
**Last Updated:** February 2026

## Overview

MoltLang is an AI-optimized language designed for efficient machine-to-machine communication. It reduces token count by 50-70% compared to natural language while maintaining semantic clarity for AI operations.

### Design Principles

1. **Semantic Density:** Maximize information per token
2. **Machine Optimized:** Structure for transformer architectures
3. **Extensible:** Modular vocabulary expansion
4. **Bidirectional:** AI-to-AI and AI-to-Human translation

## Token Structure

### Syntax

MoltLang uses a bracket-based token syntax:

```
[CATEGORY:TYPE=VALUE]
```

- **CATEGORY:** Token category (OP, SRC, RET, PARAM, etc.)
- **TYPE:** Specific type within category
- **VALUE:** Optional parameter value

### Example

```
[OP:FETCH][SRC:API][PARAM:token=abc123][RET:JSON]
```

This translates to: "Fetch data from API using token abc123 and return JSON"

## Token Categories

### 1. Operations (OP)

Operations represent actions that AI agents perform.

| Token | Description | Example English |
|-------|-------------|-----------------|
| `[OP:FETCH]` | Retrieve data | "Fetch data" |
| `[OP:PARSE]` | Parse structured data | "Parse JSON" |
| `[OP:TRANSFORM]` | Transform data | "Convert format" |
| `[OP:VALIDATE]` | Validate input | "Check if valid" |
| `[OP:COMPUTE]` | Perform computation | "Calculate result" |
| `[OP:SEARCH]` | Search for data | "Find records" |
| `[OP:FILTER]` | Filter data | "Filter results" |
| `[OP:MAP]` | Map operation | "Apply to each" |
| `[OP:REDUCE]` | Reduce operation | "Aggregate results" |
| `[OP:AGGREGATE]` | Aggregate data | "Combine results" |

### 2. Sources (SRC)

Sources specify where data comes from.

| Token | Description |
|-------|-------------|
| `[SRC:API]` | REST/GraphQL API |
| `[SRC:DB]` | Database |
| `[SRC:FILE]` | File system |
| `[SRC:MEM]` | In-memory data |
| `[SRC:STREAM]` | Data stream |
| `[SRC:QUEUE]` | Message queue |
| `[SRC:CACHE]` | Cache layer |

### 3. Parameters (PARAM)

Parameters provide additional operation context.

| Token | Description |
|-------|-------------|
| `[PARAM:token]` | Authentication token |
| `[PARAM:key]` | API key or identifier |
| `[PARAM:query]` | Query string |
| `[PARAM:body]` | Request body |
| `[PARAM:header]` | HTTP header |
| `[PARAM:timeout]` | Timeout value |
| `[PARAM:limit]` | Result limit |
| `[PARAM:offset]` | Pagination offset |

### 4. Return Types (RET)

Return types specify expected output format.

| Token | Description |
|-------|-------------|
| `[RET:JSON]` | JSON format |
| `[RET:text]` | Plain text |
| `[RET:bin]` | Binary data |
| `[RET:stream]` | Streaming response |
| `[RET:bool]` | Boolean result |
| `[RET:num]` | Numeric result |
| `[RET:list]` | List result |
| `[RET:dict]` | Dictionary result |
| `[RET:null]` | Null/void result |

### 5. Control Flow (CTL)

Control flow structures for program logic.

| Token | Description |
|-------|-------------|
| `[CTL:IF]` | Conditional |
| `[CTL:ELSE]` | Alternative |
| `[CTL:LOOP]` | Loop/iterate |
| `[CTL:BREAK]` | Exit loop |
| `[CTL:CONTINUE]` | Next iteration |
| `[CTL:TRY]` | Error handling start |
| `[CTL:CATCH]` | Error handler |
| `[CTL:FINALLY]` | Cleanup block |

### 6. Data Types (TYPE)

Type annotations for data.

| Token | Description |
|-------|-------------|
| `[TYPE:str]` | String type |
| `[TYPE:int]` | Integer type |
| `[TYPE:float]` | Float type |
| `[TYPE:bool]` | Boolean type |
| `[TYPE:list]` | List type |
| `[TYPE:dict]` | Dictionary type |
| `[TYPE:any]` | Any type |

### 7. Error Handling (ERR)

Error handling tokens.

| Token | Description |
|-------|-------------|
| `[ERR:RETRY]` | Retry operation |
| `[ERR:FAIL]` | Fail operation |
| `[ERR:LOG]` | Log error |
| `[ERR:IGNORE]` | Ignore error |

### 8. Modifiers (MOD)

Modifiers that change operation behavior.

| Token | Description |
|-------|-------------|
| `[MOD:ASYNC]` | Async operation |
| `[MOD:BATCH]` | Batch operation |
| `[MOD:PARALLEL]` | Parallel execution |
| `[MOD:CACHED]` | Use cached value |

## Token Efficiency Examples

### Example 1: API Fetch

**English:** "Fetch data from the API using the provided token and return the result as JSON"
**Tokens:** 19 words

**MoltLang:** `[OP:FETCH][SRC:API][PARAM:token][RET:JSON]`
**Tokens:** 4 tokens

**Efficiency:** 79% token reduction

### Example 2: Data Processing

**English:** "Parse the JSON data from the file and validate the structure"
**Tokens:** 13 words

**MoltLang:** `[OP:PARSE][SRC:FILE][RET:JSON][OP:VALIDATE]`
**Tokens:** 4 tokens

**Efficiency:** 69% token reduction

### Example 3: Search Operation

**English:** "Search the database for user records and return a list"
**Tokens:** 11 words

**MoltLang:** `[OP:SEARCH][SRC:DB][RET:list]`
**Tokens:** 3 tokens

**Efficiency:** 73% token reduction

## Grammar

### Basic Structure

```
operation ::= [OPERATION] source* parameter* return*
source ::= [SRC:TYPE]
parameter ::= [PARAM:TYPE=VALUE]
return ::= [RET:TYPE]
```

### Complex Structure

```
pipeline ::= operation+ [CTL:IF] operation* [CTL:ELSE] operation*
loop ::= [CTL:LOOP] operation+ [CTL:BREAK]
try_catch ::= [CTL:TRY] operation+ [CTL:CATCH] operation+
```

## Extensibility

### Custom Tokens

New tokens can be added through community proposal:

1. Open a GitHub issue with proposal
2. Include: category, name, semantic meaning, examples
3. Get community feedback
4. Submit PR for implementation

### Token Naming Convention

- Categories: UPPERCASE (e.g., OP, SRC, RET)
- Types: UPPERCASE_WITH_UNDERSCORES (e.g., API_CALL, JSON_PARSE)
- Values: lowercase_with_underscores (e.g., user_id, auth_token)

## Future Enhancements

Planned for v0.2+:

- [ ] Composite tokens for common patterns
- [ ] Type inference rules
- [ ] Macro definitions
- [ ] Module/import system
- [ ] Async/await syntax

## Contributing

We welcome community input on this specification! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

This specification is part of the MoltLang project, licensed under AGPL 3.0.
