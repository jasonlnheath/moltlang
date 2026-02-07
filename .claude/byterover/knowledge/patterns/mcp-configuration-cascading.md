# MCP Configuration Cascading Pattern

**Status:** ✅ Validated
**Date:** 2026-02-07
**Context:** Claude Code MCP server configuration

## Overview

`.mcp.json` files cascade from parent directories to child projects, enabling shared MCP server configuration across multiple projects without duplication.

## Pattern

### Create Parent-Level MCP Configuration

Place `.mcp.json` at a parent directory level to make MCP servers available to all subdirectories:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["path/to/mcp-server/dist/index.js", "--stdio"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

### Example: MoltLang for All Projects Under c:\dev

**File:** `c:\dev\.mcp.json`

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

**Result:** All projects under `c:\dev` (e.g., `c:\dev\heathaudio`, `c:\dev\moltlang`) now have access to MoltLang MCP tools.

## Key Points

1. **Cascading:** `.mcp.json` files are inherited from parent directories
2. **Override:** Child project `.mcp.json` files can extend/override parent configuration
3. **Absolute Paths:** Use absolute paths in parent-level configs to avoid relative path issues
4. **Restart Required:** Restart Claude Code after adding/modifying `.mcp.json` files

## Configuration Hierarchy

```
c:\dev\.mcp.json          ← Shared MCP servers (MoltLang, etc.)
  ├── heathaudio\
  │   └── .mcp.json       ← Project-specific MCP servers (extends parent)
  ├── moltlang\
  │   └── .mcp.json       ← Project-specific MCP servers (extends parent)
  └── other-project\
      └── (inherits from parent)
```

## Use Cases

- Shared development tools (MoltLang, code execution, debug bridge)
- Organization-wide MCP servers
- Common utilities across related projects

## Related Patterns

- N/A

## References

- Claude Code MCP documentation
- MoltLang MCP: `c:\dev\moltlang\mcp-server\`
