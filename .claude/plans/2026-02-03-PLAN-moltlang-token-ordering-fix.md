# MoltLang Token Ordering & Quality Improvement Plan

## Problem Analysis

After testing with both Haiku and GLM-4.5-Air, we've identified that the robustness improvements successfully added CTL, ERR, and TYPE token detection. However, two main issues remain:

1. **Token Ordering** - Tokens are output in category order, not semantic flow order
2. **Extra Tokens** - Adding CTL:else, ERR:fail, and extra TYPE tokens that weren't requested

### Current Token Addition Order (from exploration)

The translator adds tokens in this fixed category sequence:
```
Modifiers → Control Flow → Error Handling → Operations → Sources → Parameters → Returns → Types
```

**Example:** `"Parse JSON data from file, validate structure, transform to CSV"`

**Current Output:** `[OP:parse][OP:transform][OP:validate][SRC:file][RET:json]`

**Expected:** `[OP:parse][SRC:file][RET:json][OP:validate][OP:transform][RET:text]`

### Root Cause

From `src/moltlang/translator.py` - tokens are grouped by category, not by semantic flow. Each token category is detected independently and appended in a fixed order, regardless of how the operations relate to each other in the input.

---

## Proposed Solutions

### Option A: Semantic Token Grouping (Recommended)

**Approach:** Track which source/return type belongs to which operation, then output them grouped.

**Example:**
```
Input: "Parse JSON from file, validate it, transform to CSV"
→ Parse: [OP:parse][SRC:file][RET:json]
→ Validate: [OP:validate][RET:json]
→ Transform: [OP:transform][RET:text]
```

**Pros:**
- Preserves semantic meaning of each operation
- Clearer token boundaries
- Easier for receiving agent to understand

**Cons:**
- More complex implementation
- Requires tracking operation-source-return relationships

### Option B: Pipeline Ordering (Alternative)

**Approach:** Reorder tokens to match expected flow: `OP → SRC → RET` for each operation.

**Pros:**
- Simpler to implement
- Matches expected test format

**Cons:**
- Still loses some semantic grouping
- May not handle complex cases well

### Option C: Minimal Fix (Quickest)

**Approach:** Only fix the extra tokens issue (CTL:else, ERR:fail) and leave ordering as-is.

**Pros:**
- Minimal code changes
- Fast to implement

**Cons:**
- Doesn't solve the ordering problem
- Tests would still show "partial" matches

---

## File: `src/moltlang/translator.py`

### Key Section: `_analyze_and_translate()` (lines 147-335)

Current implementation groups tokens by category. Changes would depend on chosen approach.

---

## File: `src/moltlang/tokens.py`

### TokenSequence Class

May need enhancement to support grouped or ordered token output.

---

## Decision Needed

Which approach should we prioritize?

1. **Option A** - Semantic token grouping (most comprehensive, maintains meaning)
2. **Option B** - Pipeline ordering reordering (simpler, better test alignment)
3. **Option C** - Minimal fix only extra tokens (quickest, partial improvement)

---

## Verification

After implementation, re-run the 8 progressive tests with Haiku/GLM-4.5-Air and measure improvement in:
- Exact matches (currently 1/8)
- Partial matches (currently 7/8)
- Token accuracy
- Semantic preservation
