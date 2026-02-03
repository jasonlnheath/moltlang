"""
MoltLang MCP Server implementation.

This module implements the Model Context Protocol server for MoltLang translation.
"""

import asyncio
import json
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from moltlang import MoltTranslator, MoltValidator, translate_to_molt, translate_from_molt


class MCPServer:
    """
    Model Context Protocol server for MoltLang.

    Provides translation endpoints for AI agents to communicate using MoltLang.
    """

    def __init__(self):
        """Initialize the MCP server."""
        self.translator = MoltTranslator()
        self.validator = MoltValidator()
        self.tools = self._register_tools()

    def _register_tools(self) -> list[Tool]:
        """Register available MCP tools."""
        return [
            Tool(
                name="translate_to_molt",
                description="Translate human language text to MoltLang (AI-optimized language)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Human language text to translate to MoltLang",
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Source language code (default: 'en' for English)",
                            "default": "en",
                        },
                    },
                    "required": ["text"],
                },
            ),
            Tool(
                name="translate_from_molt",
                description="Translate MoltLang to human language text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "molt_text": {
                            "type": "string",
                            "description": "MoltLang text to translate to human language",
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code (default: 'en' for English)",
                            "default": "en",
                        },
                    },
                    "required": ["molt_text"],
                },
            ),
            Tool(
                name="validate_translation",
                description="Validate a MoltLang translation and return quality metrics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "original": {
                            "type": "string",
                            "description": "Original text before translation",
                        },
                        "translated": {
                            "type": "string",
                            "description": "Translated text to validate",
                        },
                    },
                    "required": ["original", "translated"],
                },
            ),
            Tool(
                name="list_tokens",
                description="List all available MoltLang tokens, optionally filtered by type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "token_type": {
                            "type": "string",
                            "description": "Filter by token type (e.g., 'OP', 'SRC', 'RET', 'PARAM')",
                        },
                    },
                },
            ),
            Tool(
                name="get_token_efficiency",
                description="Calculate token efficiency for a translation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "english_text": {
                            "type": "string",
                            "description": "English text to analyze",
                        },
                        "molt_text": {
                            "type": "string",
                            "description": "MoltLang translation to analyze",
                        },
                    },
                    "required": ["english_text", "molt_text"],
                },
            ),
        ]

    async def handle_translate_to_molt(self, arguments: dict[str, Any]) -> str:
        """Handle translate_to_molt tool call."""
        text = arguments.get("text", "")
        if not text:
            return json.dumps({"error": "Missing 'text' argument"})

        result = self.translator.translate_to_molt(text)

        return json.dumps(
            {
                "moltlang": result.text,
                "token_count": result.token_count,
                "original_token_count": result.original_token_count,
                "efficiency": result.token_efficiency,
                "confidence": result.confidence,
            }
        )

    async def handle_translate_from_molt(self, arguments: dict[str, Any]) -> str:
        """Handle translate_from_molt tool call."""
        molt_text = arguments.get("molt_text", "")
        if not molt_text:
            return json.dumps({"error": "Missing 'molt_text' argument"})

        result = self.translator.translate_from_molt(molt_text)

        return json.dumps(
            {
                "translation": result.text,
                "token_count": result.token_count,
                "confidence": result.confidence,
            }
        )

    async def handle_validate_translation(self, arguments: dict[str, Any]) -> str:
        """Handle validate_translation tool call."""
        original = arguments.get("original", "")
        translated = arguments.get("translated", "")

        if not original or not translated:
            return json.dumps({"error": "Missing 'original' or 'translated' argument"})

        quality = self.validator.validate_translation(original, translated)

        return json.dumps(
            {
                "is_valid": quality.is_valid,
                "score": quality.score,
                "token_efficiency": quality.token_efficiency,
                "confidence": quality.confidence,
                "issues": [
                    {"type": issue.type.value, "message": issue.message, "severity": issue.severity}
                    for issue in quality.issues
                ],
                "metrics": quality.metrics,
            }
        )

    async def handle_list_tokens(self, arguments: dict[str, Any]) -> str:
        """Handle list_tokens tool call."""
        from moltlang.tokens import TokenRegistry

        registry = TokenRegistry()
        token_type_filter = arguments.get("token_type")

        # Note: This is a simplified implementation
        # A full implementation would properly filter by token type

        from moltlang.tokens import TokenType

        if token_type_filter:
            token_type_prefix = token_type_filter.upper()
            tokens = [t for t in TokenType if t.name.startswith(token_type_prefix)]
        else:
            tokens = list(TokenType)

        return json.dumps(
            {"tokens": [{"name": t.name, "value": t.value} for t in tokens], "count": len(tokens)}
        )

    async def handle_get_token_efficiency(self, arguments: dict[str, Any]) -> str:
        """Handle get_token_efficiency tool call."""
        english_text = arguments.get("english_text", "")
        molt_text = arguments.get("molt_text", "")

        if not english_text or not molt_text:
            return json.dumps({"error": "Missing 'english_text' or 'molt_text' argument"})

        # Count tokens
        english_tokens = len(english_text.split())
        molt_tokens = molt_text.count("[")  # Each token starts with [

        efficiency = 1.0 - (molt_tokens / english_tokens) if english_tokens > 0 else 0.0

        return json.dumps(
            {
                "english_tokens": english_tokens,
                "molt_tokens": molt_tokens,
                "efficiency": efficiency,
                "reduction_percentage": efficiency * 100,
            }
        )

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle a tool call request."""
        tool_name = request.params.name
        arguments = request.params.arguments or {}

        try:
            if tool_name == "translate_to_molt":
                result = await self.handle_translate_to_molt(arguments)
            elif tool_name == "translate_from_molt":
                result = await self.handle_translate_from_molt(arguments)
            elif tool_name == "validate_translation":
                result = await self.handle_validate_translation(arguments)
            elif tool_name == "list_tokens":
                result = await self.handle_list_tokens(arguments)
            elif tool_name == "get_token_efficiency":
                result = await self.handle_get_token_efficiency(arguments)
            else:
                result = json.dumps({"error": f"Unknown tool: {tool_name}"})

            return CallToolResult(content=[TextContent(type="text", text=result)])
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
            )

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools."""
        return ListToolsResult(tools=self.tools)


# Server initialization

async def main():
    """Main entry point for the MCP server."""
    server = MCPServer()

    # Use stdio transport for MCP
    from mcp.server import Server

    mcp_server = Server("moltlang")

    @mcp_server.list_tools()
    async def list_tools_handler() -> list[Tool]:
        return await server.list_tools(ListToolsRequest())

    @mcp_server.call_tool()
    async def call_tool_handler(name: str, arguments: dict) -> list[TextContent]:
        request = CallToolRequest(
            jsonrpc="2.0",
            id=1,
            params=type("Params", (), {"name": name, "arguments": arguments})(),
        )
        result = await server.call_tool(request)
        return [c for c in result.content if isinstance(c, TextContent)]

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="moltlang",
                server_version="0.1.0",
                capabilities=mcp_server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
