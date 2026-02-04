# MoltLang Weak LLM Robustness Plan

## Problem Statement

After testing MoltLang with Haiku (a weaker LLM), several token categories were consistently missed:

| Failure | Tokens Missed | Impact |
|---------|---------------|--------|
| Control Flow | `CTL:try`, `CTL:catch`, `CTL:finally` | No error handling structure |
| Error Handling | `ERR:retry`, `ERR:log`, `ERR:fail` | No error recovery |
| Type System | `TYPE:str`, `TYPE:int`, `TYPE:list` | Type constraints lost |
| Parameter Values | `PARAM:key=12345`, `PARAM:timeout=30` | Values dropped |
| Return Types | Specific types default to generic | Meaning ambiguity |

**Result**: 1/8 tests passed, 3/8 partial, 4/8 failed.

## Root Cause

The translator in `src/moltlang/translator.py` uses **simple keyword matching** with limited synonym sets. Weak LLMs express concepts indirectly rather than using exact keywords.

## Solution Overview

Add **5 robustness layers** to make MoltLang foolproof for weaker LLMs:

1. **Synonym Expansion** - More English phrases mapped to tokens
2. **Contextual Matching** - Detect intent from surrounding words
3. **Fallback Patterns** - Intelligent defaults when matching fails
4. **Enhanced Parameter Extraction** - Better regex for values
5. **Improved Confidence Scoring** - Semantic completeness vs token count

---

## Implementation

### File: `C:\dev\moltlang\src\moltlang\translator.py`

#### Change 1: Add Control Flow Token Detection

**Location**: `_analyze_and_translate()` method, after line 168 (after modifier detection)

**Add**:
```python
# Control flow detection (NEW)
if any(word in text_lower for word in [
    "try", "attempt", "attempting", "trying to", "give it a shot"
]):
    tokens.add(Token(type=TokenType.CTL_TRY))

if any(word in text_lower for word in [
    "catch", "handle error", "on error", "except", "when error",
    "on failure", "error handler"
]):
    tokens.add(Token(type=TokenType.CTL_CATCH))

if any(word in text_lower for word in [
    "finally", "cleanup", "afterwards", "always do"
]):
    tokens.add(Token(type=TokenType.CTL_FINALLY))
```

#### Change 2: Add Error Handling Token Detection

**Location**: Immediately after CTL detection

**Add**:
```python
# Error handling detection (NEW)
if any(word in text_lower for word in [
    "retry", "try again", "reattempt", "attempt again", "keep trying"
]):
    tokens.add(Token(type=TokenType.ERR_RETRY))

if any(word in text_lower for word in [
    "log", "logging", "record", "write log", "log entry", "log error"
]):
    tokens.add(Token(type=TokenType.ERR_LOG))

if any(word in text_lower for word in [
    "fail", "failure", "throw error", "raise error", "abort on error"
]):
    tokens.add(Token(type=TokenType.ERR_FAIL))
```

#### Change 3: Add Type System Token Detection

**Location**: After RET detection (around line 220)

**Add**:
```python
# Type constraint detection (NEW)
import re

if any(word in text_lower for word in [
    "type str", "type string", "string type", "as string", "to string"
]) or re.search(r'\btype\s*[:=]\s*str(?:ing)?\b', text_lower):
    tokens.add(Token(type=TokenType.TYPE_STR))

if any(word in text_lower for word in [
    "type int", "integer type", "as integer", "to integer"
]) or re.search(r'\btype\s*[:=]\s*int(?:eger)?\b', text_lower):
    tokens.add(Token(type=TokenType.TYPE_INT))

if any(word in text_lower for word in [
    "type list", "list type", "array type", "as list", "to list"
]) or re.search(r'\btype\s*[:=]\s*list\b', text_lower):
    tokens.add(Token(type=TokenType.TYPE_LIST))

if any(word in text_lower for word in [
    "type dict", "dict type", "map type", "as dict", "to dict"
]) or re.search(r'\btype\s*[:=]\s*dict\b', text_lower):
    tokens.add(Token(type=TokenType.TYPE_DICT))
```

#### Change 4: Enhance Parameter Extraction

**Location**: Replace lines 200-205 (current timeout-only detection)

**Replace with**:
```python
# Enhanced parameter extraction
import re

# PARAM:TIMEOUT - Multiple patterns
timeout_match = re.search(
    r'timeout\s*(?:of|:|=)?\s*(\d+)\s*(?:seconds?|secs?|s)?',
    text_lower
)
if timeout_match:
    tokens.add(Token(type=TokenType.PARAM_TIMEOUT, value=timeout_match.group(1)))

# PARAM:LIMIT
limit_match = re.search(
    r'(?:limit|max|maximum)\s*(?:of|:|=)?\s*(\d+)',
    text_lower
)
if limit_match:
    tokens.add(Token(type=TokenType.PARAM_LIMIT, value=limit_match.group(1)))

# PARAM:KEY
key_match = re.search(
    r'(?:api\s+)?key\s*(?:of|:|=)?\s*["\']?([\w\-]+)["\']?',
    text_lower
)
if key_match:
    tokens.add(Token(type=TokenType.PARAM_KEY, value=key_match.group(1)))

# PARAM:QUERY
query_match = re.search(
    r'(?:query|search|find)\s+(?:for|:|=)?\s*["\']?([^"\']+)["\']?',
    text_lower
)
if query_match:
    tokens.add(Token(type=TokenType.PARAM_QUERY, value=query_match.group(1)))
```

#### Change 5: Add Fallback Rules Method

**Location**: New method after `_calculate_confidence()`

**Add**:
```python
def _apply_fallback_rules(self, text: str, tokens: TokenSequence) -> TokenSequence:
    """Apply fallback rules when direct matching fails."""
    text_lower = text.lower()

    # Fallback 1: "safe" or "careful" implies error handling
    if any(word in text_lower for word in ["safe", "careful", "graceful", "handle"]):
        if not any(t.type.value.startswith("CTL:") for t in tokens.tokens):
            tokens.add(Token(type=TokenType.CTL_TRY))
            tokens.add(Token(type=TokenType.CTL_CATCH))

    # Fallback 2: "ensure" or "guarantee" implies validation
    if any(word in text_lower for word in ["ensure", "guarantee", "verify"]):
        if not any(t.type == TokenType.OP_VALIDATE for t in tokens.tokens):
            tokens.add(Token(type=TokenType.OP_VALIDATE))

    return tokens
```

**Then modify `_analyze_and_translate()` to call it** (before return statement):
```python
# Apply fallback rules before returning
tokens = self._apply_fallback_rules(text, tokens)
return tokens
```

#### Change 6: Improve Confidence Scoring

**Location**: Replace `_calculate_confidence()` method (lines 314-332)

**Replace with**:
```python
def _calculate_confidence(self, original: str, tokens: TokenSequence) -> float:
    """Calculate confidence based on semantic completeness."""
    if len(tokens) == 0:
        return 0.0

    # Base score from token count
    base_score = min(0.95, 0.5 + (len(tokens) * 0.1))

    # Semantic completeness bonus
    has_operation = any("OP:" in t.type.value for t in tokens.tokens)
    has_source = any("SRC:" in t.type.value for t in tokens.tokens)
    has_return = any("RET:" in t.type.value for t in tokens.tokens)

    completeness = 0.0
    if has_operation:
        completeness += 0.3
    if has_source or has_return:
        completeness += 0.3
    if has_operation and (has_source or has_return):
        completeness += 0.2

    return round(min(1.0, base_score + completeness), 2)
```

---

### File: `C:\dev\moltlang\tests\test_weak_llm_robustness.py` (NEW)

Create comprehensive test suite covering:

1. **Synonym Expansion Tests**
   - Control flow variations (try/attempt/give it a shot)
   - Error handling variations (retry/try again/reattempt)
   - Type constraint variations (type str/string type/as string)

2. **Parameter Extraction Tests**
   - Timeout formats (timeout 30, timeout of 30, timeout:30)
   - Key patterns (API key abc123, key: xyz789)
   - Limit patterns (limit 50, max 100)

3. **Fallback Pattern Tests**
   - Safe operation adds error handling
   - Ensure adds validation
   - Questions default to search

4. **Backward Compatibility Tests**
   - Existing tests still pass
   - No breaking changes

---

## Implementation Order

1. **Phase 1**: Synonym Expansion (CTL, ERR, TYPE tokens)
2. **Phase 2**: Enhanced Parameter Extraction
3. **Phase 3**: Fallback Patterns
4. **Phase 4**: Improved Confidence Scoring
5. **Phase 5**: Test Suite

---

## Verification

### Test the specific failures from Haiku:

```python
# Test 004: Error Handling - should now work
translate_to_molt("Try to fetch from API, retry on failure, otherwise log error")
# Expected: [CTL:try][OP:fetch][SRC:api][CTL:catch][ERR:retry][ERR:log]

# Test 006: Type System - should now work
translate_to_molt("Parse data and ensure it returns a properly typed list of strings")
# Expected: [OP:parse][RET:list][TYPE:str]

# Test 003: Parameters - should now work
translate_to_molt("Search database for user with ID 12345")
# Expected: [OP:search][SRC:db][PARAM:key=12345][RET:dict]
```

### Run existing tests:
```bash
python -m pytest tests/test_translator.py -v
```

### Run new robustness tests:
```bash
python -m pytest tests/test_weak_llm_robustness.py -v
```

---

## Expected Impact

| Test | Before | After |
|------|--------|-------|
| Control Flow (CTL) | ❌ Missing | ✅ Detected |
| Error Handling (ERR) | ❌ Missing | ✅ Detected |
| Type System (TYPE) | ❌ Missing | ✅ Detected |
| Parameter Values | ⚠️ Dropped | ✅ Extracted |
| Return Types | ⚠️ Generic | ✅ Specific |

**Target**: 6-8/8 tests passing (up from 1/8)
