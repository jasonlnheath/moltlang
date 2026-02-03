# MoltLang MCP Tools Fix - Implementation Plan

## Root Cause

The TypeScript MCP server (`mcp-server/src/utils/python.ts`) expects Python functions to return `TranslationResult` objects with properties like `result.text`, `result.token_count`, etc. However, the convenience function `translate_to_molt()` in `src/moltlang/__init__.py` returns only a string, causing runtime errors.

## Implementation Steps

### Step 1: Add Result-Returning Functions to Python Module

**File:** `C:\dev\moltlang\src\moltlang\__init__.py`

Add two new functions that return full `TranslationResult` objects:

```python
def translate_to_molt_result(text: str, config: MoltConfig | None = None) -> TranslationResult:
    """Translate to MoltLang and return full TranslationResult (for MCP/bridge usage)."""
    translator = _get_translator()
    return translator.translate_to_molt(text, config)

def translate_from_molt_result(molt_text: str, config: MoltConfig | None = None) -> TranslationResult:
    """Translate from MoltLang and return full TranslationResult (for MCP/bridge usage)."""
    translator = _get_translator()
    return translator.translate_from_molt(molt_text, config)
```

Update `__all__` to export the new functions.

### Step 2: Update Python Bridge to Use New Functions

**File:** `C:\dev\moltlang\mcp-server\src\utils\python.ts`

Update `translateToMolt()` and `translateFromMolt()` to call the new result-returning functions:

```typescript
// Change from: translate_to_molt("${text}")
// To: translate_to_molt_result("${text}")
```

### Step 3: Add Debug Logging

**File:** `C:\dev\moltlang\mcp-server\src\handlers\translate.ts`

Add console.error logging for debugging translation issues.

### Step 4: Rebuild TypeScript Server

```bash
cd C:/dev/moltlang/mcp-server
npm run build
```

### Step 5: Verify Python Bridge Works

```bash
python -c "from moltlang import translate_to_molt_result; result = translate_to_molt_result('Fetch data from API'); print(result.text, result.token_count)"
```

### Step 6: Test MCP Server Startup

```bash
node C:/dev/moltlang/mcp-server/dist/index.js --stdio
```

Server should start without errors and show "MoltLang MCP Server running on stdio".

### Step 7: Verify Tools Registration

Send MCP `tools/list` request via stdin. Expected response should include 5 tools:
- `molt` - English to MoltLang
- `unmolt` - MoltLang to English
- `validate_molt` - Validate translation
- `list_tokens` - List available tokens
- `get_efficiency` - Calculate efficiency

### Step 8: Test Each Tool

Test each tool with MCP `tools/call` requests:
- `molt`: `{"text": "Fetch data from API and return JSON"}`
- `unmolt`: `{"molt": "[OP:FETCH][SRC:API][RET:JSON]"}`
- `validate_molt`: `{"original": "Fetch data", "molt": "[OP:FETCH][SRC:API]"}`
- `list_tokens`: `{"category": "OP"}`
- `get_efficiency`: `{"english": "Fetch data", "molt": "[OP:FETCH]"}`

### Step 9: Update Documentation

**File:** `C:\dev\moltlang\mcp-server\README.md`

Add installation, configuration, and testing instructions.

## Verification

After implementation, verify:
1. Python bridge returns `TranslationResult` objects
2. MCP server starts without errors
3. All 5 tools visible in tool list
4. Each tool executes successfully
5. Tools return expected results with metadata

## Critical Files

- `C:\dev\moltlang\src\moltlang\__init__.py` - Add new result-returning functions
- `C:\dev\moltlang\mcp-server\src\utils\python.ts` - Update to call new functions
- `C:\dev\moltlang\mcp-server\src\handlers\translate.ts` - Add debug logging
- `C:\dev\moltlang\src\moltlang\translator.py` - Reference for TranslationResult structure

## Expected Configuration

```json
{
  "mcpServers": {
    "moltlang": {
      "command": "node",
      "args": ["C:/dev/moltlang/mcp-server/dist/index.js", "--stdio"]
    }
  }
}
```

## Success Criteria

- MCP server starts cleanly
- All 5 tools appear in tool list
- Tools execute without errors
- Results include token efficiency metadata
