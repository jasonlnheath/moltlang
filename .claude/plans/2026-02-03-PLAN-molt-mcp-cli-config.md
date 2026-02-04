# Plan: Configure MoltLang MCP Server for Claude Code CLI

## Problem Statement

The MoltLang MCP server implementation is complete and functional (5 tools: `molt`, `unmolt`, `validate_molt`, `list_tokens`, `get_efficiency`), but the tools do not appear in Claude Code CLI's `/mcp` command output.

## Root Cause

Claude Code CLI requires MCP server configuration in a project-local `.claude/settings.json` file. Currently, no such configuration exists in the MoltLang project.

---

## Implementation

### Create Claude Code CLI MCP Configuration

**File to create:** `C:\dev\moltlang\.claude\settings.json`

**Content:**
```json
{
  "mcpServers": {
    "moltlang": {
      "command": "node",
      "args": ["C:/dev/moltlang/mcp-server/dist/index.js", "--stdio"],
      "env": {
        "PYTHONPATH": "C:/dev/moltlang/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Why these settings:**
- `command: node` - Runs the Node.js MCP server
- `args` - Points to the built TypeScript MCP server with stdio transport
- `PYTHONPATH` - Ensures Python can import the `moltlang` module from `src/`
- `PYTHONUNBUFFERED` - Enables real-time output from Python subprocess

---

## Critical Files

| File | Purpose |
|------|---------|
| `.claude/settings.json` | **CREATE** - MCP server configuration |
| `mcp-server/dist/index.js` | Built MCP server (verify exists) |
| `src/moltlang/__init__.py` | Exports `translate_to_molt_result`, `translate_from_molt_result` |
| `mcp-server/src/handlers/translate.ts` | Tool handlers calling Python bridge |

---

## Verification Steps

1. Create `.claude/settings.json` with the configuration above
2. Restart Claude Code CLI
3. Run `/mcp` command
4. Verify `moltlang` server appears with 5 tools
5. Test tool: `molt` with English text input

---

## Troubleshooting

**If tools don't appear:**
- Check JSON syntax is valid
- Verify paths use forward slashes
- Test MCP server manually: `node mcp-server/dist/index.js --stdio`

**If Python errors occur:**
- Verify `PYTHONPATH` includes `C:/dev/moltlang/src`
- Test: `python -c "from moltlang import translate_to_molt_result"`
