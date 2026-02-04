# MoltLang Token Ordering Fix - Semantic Grouping (Improved)

## Problem Statement

Current implementation groups tokens by **category**, not **semantic flow**:

**Test 002 Example:**
- English: "Parse JSON data from file, validate structure, transform to CSV"
- Current: `[OP:parse][OP:transform][OP:validate][SRC:file][RET:json]`
- Expected: `[OP:parse][SRC:file][RET:json][OP:validate][OP:transform][RET:text]`

**Root Cause:** All operations are detected first, then all sources, then all returns - losing the semantic relationship between them.

## Solution: Position-Based Semantic Grouping

### Core Insight

Parse the text **in order** and build operation groups based on **text position**. Each operation picks up the source/return tokens that appear **near it** in the original text.

### Token Ordering Rules

1. **Modifiers** (MOD) → Global scope, output first
2. **Control Flow** (CTL) → Wrap operations, output second
3. **Error Handling** (ERR) → After CTL
4. **Operation Groups** → Each operation with its associated SRC/RET/PARAM:
   - `[OP:operation][SRC:source][RET:return][PARAM:params]`
5. **Type Constraints** (TYPE) → At end

### Explicit Pairing Rules

| Pattern | Pairing | Example |
|---------|---------|---------|
| "Parse JSON" | OP + RET | `[OP:parse][RET:json]` |
| "from file" | OP + SRC | `[OP:fetch][SRC:file]` |
| "return JSON" | adds RET to last OP | `...[RET:json]` |
| "transform to CSV" | OP + RET | `[OP:transform][RET:text]` |

## Implementation Plan

### File: `src/moltlang/translator.py`

### Phase 1: Add Position-Tracking Detection

Create a dataclass to track token positions:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DetectedToken:
    """Token with position information for semantic grouping."""
    token: Token
    position: int  # Character position in original text
    keyword: str   # The keyword that triggered detection
```

### Phase 2: Implement `_detect_with_positions()`

Replace the current detection logic with position-tracking:

```python
def _detect_with_positions(self, text: str) -> dict[str, list[DetectedToken]]:
    """Detect all tokens with their positions in text."""
    text_lower = text.lower()
    detected = {
        "modifiers": [],
        "control": [],
        "errors": [],
        "operations": [],
        "sources": [],
        "returns": [],
        "params": [],
        "types": [],
    }

    # Operations with position tracking
    op_keywords = {
        TokenType.OP_FETCH: ["fetch", "get", "retrieve", "download"],
        TokenType.OP_PARSE: ["parse", "analyze", "extract"],
        TokenType.OP_TRANSFORM: ["transform", "convert"],
        TokenType.OP_SEARCH: ["search", "find", "lookup"],
        TokenType.OP_VALIDATE: ["validate", "verify", "check", "ensure"],
        TokenType.OP_FILTER: ["filter", "sift", "screen"],
        TokenType.OP_AGGREGATE: ["aggregate", "combine", "merge", "summarize"],
    }

    for token_type, keywords in op_keywords.items():
        for keyword in keywords:
            pos = text_lower.find(keyword)
            if pos != -1:
                detected["operations"].append(DetectedToken(
                    token=Token(type=token_type),
                    position=pos,
                    keyword=keyword
                ))
                break  # Only first match per operation type

    # Sources with position tracking
    src_keywords = {
        TokenType.SRC_API: ["api", "endpoint", "rest"],
        TokenType.SRC_DB: ["database", "db"],
        TokenType.SRC_FILE: ["file", "csv file"],
        TokenType.SRC_MEM: ["memory", "cache", "ram"],
    }

    for token_type, keywords in src_keywords.items():
        for keyword in keywords:
            pos = text_lower.find(keyword)
            if pos != -1:
                detected["sources"].append(DetectedToken(
                    token=Token(type=token_type),
                    position=pos,
                    keyword=keyword
                ))
                break

    # Returns with position tracking - IMPORTANT: detect ALL returns
    ret_keywords = {
        TokenType.RET_JSON: ["json", "object"],
        TokenType.RET_TEXT: ["csv", "text", "plain"],
        TokenType.RET_LIST: ["list", "array"],
        TokenType.RET_DICT: ["dictionary", "dict", "map"],
        TokenType.RET_BOOL: ["boolean", "bool"],
        TokenType.RET_NUM: ["number", "numeric"],
    }

    for token_type, keywords in ret_keywords.items():
        for keyword in keywords:
            # Find ALL occurrences, not just first
            start = 0
            while True:
                pos = text_lower.find(keyword, start)
                if pos == -1:
                    break
                detected["returns"].append(DetectedToken(
                    token=Token(type=token_type),
                    position=pos,
                    keyword=keyword
                ))
                start = pos + 1
            if detected["returns"]:
                break  # Only use first matching keyword set per type

    # ... similar for modifiers, control, errors, params, types

    return detected
```

### Phase 3: Implement `_build_semantic_groups()`

Group operations with their nearest source/return:

```python
def _build_semantic_groups(self, text: str, detected: dict) -> list[dict]:
    """Build operation groups based on text position."""
    text_lower = text.lower()

    # Sort operations by position
    operations = sorted(detected["operations"], key=lambda x: x.position)
    sources = sorted(detected["sources"], key=lambda x: x.position)
    returns = sorted(detected["returns"], key=lambda x: x.position)

    groups = []
    used_sources = set()
    used_returns = set()

    for i, op in enumerate(operations):
        group = {
            "operation": op.token,
            "source": None,
            "returns": [],  # Can have multiple returns per op
            "params": []
        }

        # Find nearest source BEFORE this operation (or first op gets first source)
        if i == 0 and sources:
            # First operation gets the source
            group["source"] = sources[0].token
            used_sources.add(0)
        else:
            # Check for source between previous op and this one
            prev_pos = operations[i-1].position if i > 0 else 0
            for j, src in enumerate(sources):
                if j not in used_sources and prev_pos < src.position < op.position:
                    group["source"] = src.token
                    used_sources.add(j)
                    break

        # Find returns that are "near" this operation
        # Strategy: return belongs to operation if it appears:
        # 1. Immediately after the operation keyword ("Parse JSON")
        # 2. Or before the next operation
        next_op_pos = operations[i+1].position if i+1 < len(operations) else len(text_lower)

        for j, ret in enumerate(returns):
            if j not in used_returns:
                # Check if return is between this op and next op
                if op.position < ret.position < next_op_pos:
                    group["returns"].append(ret.token)
                    used_returns.add(j)
                # Also check for "transform to CSV" pattern (op keyword followed by "to <type>")
                elif f"{op.keyword} to" in text_lower or f"{op.keyword}s to" in text_lower:
                    # This return type might follow "to"
                    to_pos = text_lower.find(" to ", op.position)
                    if to_pos != -1 and to_pos < next_op_pos:
                        if to_pos < ret.position < to_pos + 20:  # Within 20 chars of "to"
                            group["returns"].append(ret.token)
                            used_returns.add(j)

        groups.append(group)

    # Handle remaining returns - assign to last operation
    if groups:
        for j, ret in enumerate(returns):
            if j not in used_returns:
                groups[-1]["returns"].append(ret.token)

    return groups
```

### Phase 4: Implement `_flatten_groups()`

Convert groups to final token sequence:

```python
def _flatten_groups(self, detected: dict, groups: list[dict]) -> TokenSequence:
    """Flatten semantic groups into final token sequence."""
    tokens = TokenSequence()

    # 1. Modifiers first (global scope)
    for dt in detected["modifiers"]:
        tokens.add(dt.token)

    # 2. Control flow
    for dt in detected["control"]:
        tokens.add(dt.token)

    # 3. Error handling
    for dt in detected["errors"]:
        tokens.add(dt.token)

    # 4. Operation groups in order
    for group in groups:
        tokens.add(group["operation"])
        if group["source"]:
            tokens.add(group["source"])
        for ret in group["returns"]:
            tokens.add(ret)
        for param in group["params"]:
            tokens.add(param)

    # 5. Type constraints at end
    for dt in detected["types"]:
        tokens.add(dt.token)

    return tokens
```

### Phase 5: Refactor `_analyze_and_translate()`

Wire everything together:

```python
def _analyze_and_translate(self, text: str) -> TokenSequence:
    """Analyze human text and generate MoltLang tokens with semantic grouping."""
    # Step 1: Detect all tokens with positions
    detected = self._detect_with_positions(text)

    # Step 2: Build semantic groups
    groups = self._build_semantic_groups(text, detected)

    # Step 3: Flatten to final sequence
    tokens = self._flatten_groups(detected, groups)

    # Step 4: Apply fallback rules
    return self._apply_fallback_rules(text, tokens)
```

## Test Cases

| Test | Input | Expected | Key Challenge |
|------|-------|----------|---------------|
| 001 | "Fetch user data from the API and return JSON" | `[OP:fetch][SRC:api][RET:json]` | Basic single-op |
| 002 | "Parse JSON data from file, validate structure, transform to CSV" | `[OP:parse][SRC:file][RET:json][OP:validate][OP:transform][RET:text]` | Multi-op with intermediate RET |
| 003 | "Search database for user with ID 12345, return profile as dictionary" | `[OP:search][SRC:db][PARAM:key=12345][RET:dict]` | Parameter extraction |
| 004 | "Try to fetch from API, retry on failure, otherwise log error" | `[CTL:try][OP:fetch][SRC:api][CTL:catch][ERR:retry][ERR:log]` | Control flow ordering |
| 005 | "Asynchronously fetch from multiple APIs in parallel, aggregate results" | `[MOD:async][MOD:parallel][OP:fetch][SRC:api][OP:aggregate]` | Multi-modifier, multi-op |
| 006 | "Parse data and ensure it returns a properly typed list of strings" | `[OP:parse][RET:list][TYPE:str]` | Type constraints |
| 007 | "Fetch from API, parse JSON response, validate against schema, transform to user objects, filter active users, return as list" | `[OP:fetch][SRC:api][RET:json][OP:parse][OP:validate][OP:transform][OP:filter][RET:list]` | Long pipeline |
| 008 | "Try to batch process 1000 records from database in parallel, cache results, retry failed records 3 times, log final summary" | `[CTL:try][MOD:batch][MOD:parallel][OP:process][SRC:db][PARAM:limit=1000][MOD:cached][CTL:catch][ERR:retry][PARAM:times=3][ERR:log]` | Expert complexity |

## Files to Modify

| File | Changes |
|------|---------|
| `src/moltlang/translator.py` | Add DetectedToken class, refactor `_analyze_and_translate()` |

## Implementation Checklist

1. [ ] Add `DetectedToken` dataclass
2. [ ] Implement `_detect_with_positions()` helper
3. [ ] Implement `_build_semantic_groups()` helper
4. [ ] Implement `_flatten_groups()` helper
5. [ ] Refactor `_analyze_and_translate()` to use new helpers
6. [ ] Run test suite to verify
7. [ ] Test with MCP tools

## Key Improvements Over Original Plan

1. **Position-based grouping** - Uses character positions to correctly associate sources/returns with operations
2. **Multiple returns handling** - Detects ALL return type mentions, not just first
3. **Explicit pairing detection** - Handles patterns like "transform to CSV" → `[OP:transform][RET:text]`
4. **Operation ordering** - Sorts operations by text position before grouping

## Notes

- No breaking changes to external API
- Backward compatible with single-operation cases
- Performance impact minimal (same detection, smarter ordering)
