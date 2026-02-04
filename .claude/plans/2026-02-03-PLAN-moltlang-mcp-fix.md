# MCP Server Fix Plan

## Diagnosis Summary

The MCP server code works correctly — confirmed end-to-end:
- Server starts, responds to `initialize`, lists 5 tools, executes `molt` via Python bridge
- Python `translate_to_molt_result()` returns valid `TranslationResult`
- All MCP protocol messages are properly handled

**Root cause of "tools not showing up in /mcp":** The `mcpServers` config is in
`.claude/settings.json` (project-level) but Claude Code is not picking it up from
there. The global `~/.claude/settings.json` does not have any `mcpServers` key.
The working MCP servers in this environment (`git-context`, `zai-mcp-server`) are
registered through a different mechanism. The fix is to add the `moltlang` server
config to the **global** `~/.claude/settings.json`.

**Additional bugs found in code** (fix while we're at it):

| # | File | Bug |
|---|------|-----|
| 1 | `src/moltlang/tokens.py` | `TokenRegistry._custom_tokens` uses `field(default_factory=dict)` as a class variable in a non-dataclass. It becomes a `Field` object, not a `dict`. Crashes if accessed via `get()` or `list_tokens()`. |
| 2 | `mcp-server/src/utils/python.ts` | `categoryOutput` is a single-quoted string — `${category}` is NOT interpolated. The Python code gets literal `"${category}"` instead of the actual value. |
| 3 | `src/moltlang/validator.py` | `_validate_syntax` regex `^[A-Z]+:[A-Z_]+` requires uppercase only. But translator emits lowercase tokens like `[OP:fetch]`. Every translation fails validation. |
| 4 | `tests/test_translator.py` | Assertions like `TokenType.OP_FETCH.value == "OP:FETCH"` are wrong — actual value is `"OP:fetch"` (lowercase). |

---

## Files to Modify

1. **`~/.claude/settings.json`** (`/c/Users/jason/.claude/settings.json`)
   - Add `mcpServers.moltlang` block (same as what's already in project settings.json)
   - Keep all existing keys (`model`, `hooks`, `statusLine`, etc.)

2. **`src/moltlang/tokens.py`** — `TokenRegistry` class body
   - Remove broken `_custom_tokens: dict[str, Token] = field(default_factory=dict)` class var
   - Initialize `self._custom_tokens = {}` in `_initialize()`

3. **`mcp-server/src/utils/python.ts`** — `listTokens` function, the `categoryOutput` line
   - Change from single-quoted string to backtick template so `${category}` interpolates

4. **`src/moltlang/validator.py`** — `_validate_syntax` method
   - Fix regex to accept lowercase: use `re.IGNORECASE` flag or adjust pattern to `[A-Za-z]`

5. **`tests/test_translator.py`** — `TestTokenTypes` class
   - Fix assertions to match actual lowercase token values (e.g., `"OP:fetch"` not `"OP:FETCH"`)

6. **Rebuild** — run `npm run build` in `mcp-server/` after fixing python.ts

7. **Cleanup** — delete files created during diagnostic investigation:
   - `mcp-server/debug_test.mjs`
   - `mcp-server/debug_server.mjs`
   - Project root `nul` file (Windows reserved device name)

---

## Verification

1. After adding to global settings.json, restart Claude Code or run `/mcp` — should see `moltlang` server with 5 tools
2. Call `molt` tool with "Fetch data from API" — expect `[OP:fetch][SRC:api] | tokens:2 eff:50% conf:85%`
3. Call `unmolt` with `[OP:fetch][SRC:api]` — expect English translation
4. Call `validate_molt` — should pass validation (after regex fix)
5. Call `list_tokens` with and without category filter — verify category field is correct value (not literal `${category}`)
6. Run `python -m pytest tests/ -v` to verify test fixes pass
