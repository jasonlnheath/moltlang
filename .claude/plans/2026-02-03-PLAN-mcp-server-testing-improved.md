# MoltLang MCP Server Testing Plan (Revised)

**Status:** Implementation largely complete - focus on testing gaps
**Date:** February 3, 2026

---

## Executive Summary

The TypeScript MCP server is fully implemented but has **zero tests**. This plan focuses on adding comprehensive test coverage using Vitest. The Python side already has tests.

---

## Current State Summary

| Component | Status | Location |
|-----------|--------|----------|
| TypeScript MCP Server | ✅ Complete | `mcp-server/src/` |
| Python MCP Server | ✅ Complete | `src/mcp_server/` |
| Core Translation Library | ✅ Complete | `src/moltlang/` |
| Python Tests | ✅ Partial | `tests/` |
| **TypeScript Tests** | ❌ **MISSING** | `mcp-server/tests/` |
| Inter-Model Tests | ✅ 7/8 Complete | `tests/inter_model_communication.py` |

**Achieved Performance:** 79.89% average token efficiency (exceeds 50-70% goal)

---

## Critical Gaps to Address

### 1. TypeScript MCP Server Testing (Priority: HIGH)

**Current State:** Zero tests exist for the TypeScript server

**Files to Create:**
```
mcp-server/tests/
├── tools.test.ts           # Tool definition validation
├── handlers.test.ts        # Handler unit tests
├── cache.test.ts           # Cache functionality
├── python-bridge.test.ts   # Python subprocess integration
└── integration.test.ts     # Full MCP protocol tests
```

**Test Categories:**

| Test File | Coverage | Test Count |
|-----------|----------|------------|
| `tools.test.ts` | Tool schemas, validation | 5-8 |
| `handlers.test.ts` | Each of 5 tool handlers | 10-15 |
| `cache.test.ts` | TTL, expiry, stats | 5-8 |
| `python-bridge.test.ts` | Subprocess, errors | 5-8 |
| `integration.test.ts` | E2E MCP protocol | 5-8 |

---

## Implementation Tasks

### Task 1: Set Up Vitest Test Infrastructure

**Modify:** `mcp-server/package.json`
```json
{
  "devDependencies": {
    "vitest": "^2.0.0",
    "@vitest/coverage-v8": "^2.0.0"
  },
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

**Create:** `mcp-server/vitest.config.ts`

---

### Task 2: Test `tools.ts` (Pure Unit Tests)

**File:** `mcp-server/tests/tools.test.ts`

**Exports to test:**
- `MOLT_TOOLS` (array of 5 tools)
- `TOKEN_CATEGORIES` (object with 8 categories)
- `isValidMoltSyntax(molt: string)` function

**Test cases:**

| Test | Description |
|------|-------------|
| `MOLT_TOOLS has 5 tools` | Verify array length |
| `All tool descriptions <50 chars` | Token efficiency requirement |
| `Tool names are molt, unmolt, validate_molt, list_tokens, get_efficiency` | Names match handlers |
| `Each tool has inputSchema with type: object` | Valid MCP schemas |
| `TOKEN_CATEGORIES has 8 entries` | OP, SRC, RET, PARAM, CTL, TYPE, ERR, MOD |
| `isValidMoltSyntax('[OP:FETCH]') returns true` | Valid single token |
| `isValidMoltSyntax('[OP:FETCH][SRC:API]') returns true` | Valid multi-token |
| `isValidMoltSyntax('[OP:FETCH') returns false` | Unclosed bracket |
| `isValidMoltSyntax('[INVALID:X]') returns false` | Invalid category |
| `isValidMoltSyntax('') returns false` | Empty string |

---

### Task 3: Test `cache.ts` (Pure Unit Tests)

**File:** `mcp-server/tests/cache.test.ts`

**Exports to test:**
- `getCachedTranslation(text, direction)`
- `setCachedTranslation(text, direction, result, ttl?)`
- `clearExpiredCache()`
- `getCacheStats()`

**Test cases:**

| Test | Description |
|------|-------------|
| `Returns null for uncached text` | Cache miss |
| `Returns cached result after set` | Cache hit |
| `Respects direction (to_molt vs from_molt)` | Keys differ by direction |
| `Expires after TTL` | Use fake timers |
| `clearExpiredCache removes stale entries` | Only expired entries |
| `getCacheStats returns size and keys` | Accurate stats |
| `Custom TTL overrides default` | 1-second TTL expiry |

---

### Task 4: Test `handlers/translate.ts` (Mock Python Bridge)

**File:** `mcp-server/tests/handlers.test.ts`

**Requires:** Mock `utils/python.ts` functions

**Handlers to test:**
- `handleTranslateToMolt({ text })`
- `handleTranslateFromMolt({ molt })`
- `handleValidateMolt({ original, molt })`
- `handleListTokens({ category? })`
- `handleGetEfficiency({ english, molt })`

**Test cases:**

| Test | Description |
|------|-------------|
| `handleTranslateToMolt returns content array` | Response structure |
| `handleTranslateToMolt embeds metadata in response` | `tokens:X eff:Y% conf:Z%` |
| `handleTranslateFromMolt returns plain text` | No metadata |
| `handleValidateMolt returns JSON` | Validation result |
| `handleListTokens with category filters results` | Filter by OP, SRC etc |
| `handleGetEfficiency calculates percentage` | Word count vs token count |
| `Handlers return isError on exception` | Error handling |

**Mock fixture:**
```typescript
vi.mock('../utils/python.js', () => ({
  translateToMolt: vi.fn().mockResolvedValue({
    text: '[OP:FETCH][SRC:API]',
    token_count: 2,
    original_count: 5,
    efficiency: 0.6,
    confidence: 0.95
  }),
  // ... other mocks
}));
```

---

### Task 5: Test `utils/python.ts` (Integration, Requires Python)

**File:** `mcp-server/tests/python-bridge.test.ts`

**Note:** These tests require Python + moltlang installed

**Exports to test:**
- `translateToMolt(text, config?)`
- `translateFromMolt(molt, config?)`
- `validateTranslation(original, molt, config?)`
- `listTokens(category?, config?)`

**Test cases:**

| Test | Description |
|------|-------------|
| `translateToMolt returns PythonTranslationResult` | Full roundtrip |
| `translateFromMolt returns text` | Reverse translation |
| `validateTranslation returns quality object` | `is_valid`, `score`, `issues` |
| `listTokens returns all tokens` | No filter |
| `listTokens filters by category` | OP only |
| `Handles special characters in input` | Quotes, newlines escaped |
| `Timeout triggers error` | 30s default |

---

### Task 6: Test `index.ts` (Server Integration)

**File:** `mcp-server/tests/server.test.ts`

**Exports to test:**
- `createServer()` - returns configured MCP Server
- `main()` - entry point

**Test cases:**

| Test | Description |
|------|-------------|
| `createServer returns Server instance` | Server configuration |
| `Server lists 5 tools` | ListToolsRequest |
| `Server routes to correct handler` | CallToolRequest routing |
| `Unknown tool returns error` | `Unknown tool: X` |
| `Error includes isError: true` | Error response format |

---

## Files to Create

```
mcp-server/
├── vitest.config.ts           # NEW - Vitest configuration
├── tests/
│   ├── tools.test.ts          # NEW - Tool definitions tests
│   ├── cache.test.ts          # NEW - Cache tests
│   ├── handlers.test.ts       # NEW - Handler tests (mocked Python)
│   ├── python-bridge.test.ts  # NEW - Python bridge integration
│   └── server.test.ts         # NEW - Server integration
└── package.json               # MODIFY - Add vitest deps
```

---

## Files to Reference (Already Exist)

| File | Purpose |
|------|---------|
| `mcp-server/src/index.ts` | Server entry, `createServer()`, request handlers |
| `mcp-server/src/tools.ts` | `MOLT_TOOLS`, `TOKEN_CATEGORIES`, `isValidMoltSyntax` |
| `mcp-server/src/handlers/translate.ts` | 5 handler functions |
| `mcp-server/src/utils/cache.ts` | Cache implementation |
| `mcp-server/src/utils/python.ts` | Python subprocess bridge |
| `tests/test_translator.py` | Reference for Python test patterns |

---

## Verification Commands

```bash
# Install test deps
cd mcp-server && npm install vitest @vitest/coverage-v8 -D

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npx vitest run tests/tools.test.ts
```

**Success Criteria:**
- All tests pass
- >80% code coverage on handlers
- >90% code coverage on cache and tools

---

## Implementation Order

1. **Task 1:** Set up Vitest (modify package.json, create vitest.config.ts)
2. **Task 2:** Test tools.ts (pure unit tests, no mocks)
3. **Task 3:** Test cache.ts (pure unit tests, fake timers)
4. **Task 4:** Test handlers (mock Python bridge)
5. **Task 5:** Test python-bridge (requires Python installed)
6. **Task 6:** Test server integration

---

## Notes

- Tasks 2-4 can run without Python installed (mocked)
- Task 5 requires `moltlang` Python package installed
- Use `vi.mock()` for Python bridge in handler tests
- Use `vi.useFakeTimers()` for cache TTL tests
