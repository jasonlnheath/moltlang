# MoltLang MCP Server

Model Context Protocol (MCP) server for MoltLang - an AI-optimized language that reduces token consumption by 50-70% for efficient agent-to-agent communication.

## Quick Start

### Installation

```bash
npm install
npm run build
```

### Usage

```bash
# Start server (stdio transport - default for MCP clients)
npm run start:stdio

# Or start with HTTP transport
npm start
```

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "moltlang": {
      "command": "node",
      "args": ["/path/to/mcp-server/dist/index.js"]
    }
  }
}
```

## Available Tools

| Tool | Description | Token Cost |
|------|-------------|------------|
| `molt` | English→MoltLang (50-70% reduction) | ~500 tokens |
| `unmolt` | MoltLang→English | ~400 tokens |
| `validate_molt` | Validate translation quality | ~450 tokens |
| `list_tokens` | List available MoltLang tokens | ~300 tokens |
| `get_efficiency` | Calculate token efficiency | ~350 tokens |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Client (Claude, etc.)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ MCP Protocol (JSON-RPC)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              TypeScript MCP Server                      │
│  ┌──────────────────────────────────────────────┐     │
│  |  Tool Definitions (minimal descriptions)      |     │
│  └──────────────────────────────────────────────┘     │
│  ┌──────────────────────────────────────────────┐     │
│  |  Translation Handlers                        |     │
│  └──────────────┬───────────────────────────────┘     │
│                 │                                       │
│                 ▼                                       │
│  ┌──────────────────────────────────────────────┐     │
│  |  Python Bridge (spawn subprocess)            |     │
│  └──────────────┬───────────────────────────────┘     │
└─────────────────┼───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│           Python MoltLang Package                        │
│  (translator.py, tokens.py, validator.py)               │
└─────────────────────────────────────────────────────────┘
```

## Development

```bash
# Watch mode for development
npm run dev

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Token Efficiency

This server is designed to minimize MCP token overhead:

1. **Concise tool descriptions** - <50 chars per tool
2. **Minimal parameter schemas** - Only required fields
3. **Compact responses** - Abbreviated field names
4. **Caching** - Common translations cached locally

## License

AGPL-3.0 - See LICENSE in parent directory
