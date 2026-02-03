"""
MoltLang MCP Server.

This module provides a Model Context Protocol (MCP) server for MoltLang,
enabling AI agents to translate between human languages and MoltLang.
"""

__version__ = "0.1.0"

from mcp_server.server import MCPServer
from mcp_server.endpoints import MCPEndpoints

__all__ = ["MCPServer", "MCPEndpoints"]
