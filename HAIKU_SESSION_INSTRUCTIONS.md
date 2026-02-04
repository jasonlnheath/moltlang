# Haiku Session Instructions - MoltLang MCP Tool Test

## Overview
You are **claude-haiku** participating in a cross-model MoltLang test. The **claude-sonnet** session has prepared a test conversation and is waiting for your response.

## Setup Status
- MoltLang Python library: **Installed**
- MCP Server: **Built and Connected**
- All tests: **Passing** (16/16)
- MCP Tools available: `molt`, `unmolt`, `validate_molt`, `list_tokens`, `get_efficiency`

## Your Task

### Step 1: Read the handoff file
```
Read C:\dev\moltlang\moltlang_handoff.json
```

### Step 2: Find the active conversation
Look for conversation with `id: "test-001"` and `status: "awaiting_response"`

### Step 3: Read the initial message
From the messages array, find the message from `sender: "claude-sonnet"`
The content to translate: **"Fetch user data from the API and return JSON"**

### Step 4: Use the MCP `molt` tool
Call the `molt` tool with the English text:
```
Use the molt tool with: "Fetch user data from the API and return JSON"
```

Expected result format:
- `text`: The MoltLang translation
- `token_count`: Number of tokens used
- `efficiency`: Token efficiency (0-1)
- `confidence`: Confidence score (0-1)

### Step 5: Add your response to the handoff file
Add a new message to the test-001 conversation:

```json
{
  "id": "msg-2",
  "type": "molt_response",
  "sender": "claude-haiku",
  "timestamp": "2026-02-03T19:20:00Z",
  "content": "[OP:fetch][SRC:api][RET:json]",
  "metadata": {
    "token_count": 3,
    "efficiency": 0.67,
    "confidence": 0.95
  },
  "issues": []
}
```

### Step 6: Save the updated handoff file
Write the complete updated JSON back to `C:\dev\moltlang\moltlang_handoff.json`

### Step 7: Update conversation status
Change the conversation status from `"awaiting_response"` to `"completed"`

## Success Criteria
- Molt translation matches expected: `[OP:fetch][SRC:api][RET:json]`
- Token count: 3
- Efficiency > 0.5
- Confidence > 0.8

## Notes
- All token values are **lowercase** (e.g., `OP:fetch` not `OP:FETCH`)
- The MCP server is running and ready to accept tool calls
- The Sonnet session will validate your response after you save

## Troubleshooting
If the `molt` tool is not available:
1. Check `/mcp` command to see available servers
2. Verify `moltlang` server is listed
3. If not present, the MCP server may need to be restarted

---

**Ready to begin!** The handoff file is waiting at `C:\dev\moltlang\moltlang_handoff.json`
