"""
Tests for MoltLang MCP server module.
"""

import pytest
import json


class TestMCPEndpoints:
    """Test suite for MCPEndpoints class."""

    @pytest.mark.asyncio
    async def test_translate_to_molt(self):
        """Test translation to MoltLang via MCP endpoint."""
        from mcp_server.endpoints import MCPEndpoints

        endpoints = MCPEndpoints()
        response = await endpoints.translate("Fetch data from API", to_molt=True)
        assert response.success is True
        assert response.data is not None
        assert "moltlang" in response.data

    @pytest.mark.asyncio
    async def test_translate_from_molt(self):
        """Test translation from MoltLang via MCP endpoint."""
        from mcp_server.endpoints import MCPEndpoints

        endpoints = MCPEndpoints()
        response = await endpoints.translate("[OP:FETCH][SRC:API]", to_molt=False)
        assert response.success is True
        assert response.data is not None
        assert "translation" in response.data

    @pytest.mark.asyncio
    async def test_validate_endpoint(self):
        """Test validation endpoint."""
        from mcp_server.endpoints import MCPEndpoints

        endpoints = MCPEndpoints()
        response = await endpoints.validate("Fetch data", "[OP:FETCH]")
        assert response.success is True
        assert response.data is not None
        assert "is_valid" in response.data

    @pytest.mark.asyncio
    async def test_vocabulary_endpoint(self):
        """Test vocabulary endpoint."""
        from mcp_server.endpoints import MCPEndpoints

        endpoints = MCPEndpoints()
        response = await endpoints.vocabulary()
        assert response.success is True
        assert response.data is not None
        assert "tokens" in response.data
        assert response.data["count"] > 0

    @pytest.mark.asyncio
    async def test_vocabulary_with_filter(self):
        """Test vocabulary endpoint with type filter."""
        from mcp_server.endpoints import MCPEndpoints

        endpoints = MCPEndpoints()
        response = await endpoints.vocabulary(token_type="OP")
        assert response.success is True
        assert response.data["filtered_by"] == "OP"

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        from mcp_server.endpoints import MCPEndpoints

        endpoints = MCPEndpoints()
        response = await endpoints.health()
        assert response.success is True
        assert response.data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_translate_error_handling(self):
        """Test error handling in translate endpoint."""
        from mcp_server.endpoints import MCPEndpoints

        endpoints = MCPEndpoints()
        # Empty text should still succeed
        response = await endpoints.translate("", to_molt=True)
        assert response is not None


class TestEndpointResponse:
    """Test suite for EndpointResponse class."""

    def test_successful_response(self):
        """Test successful response creation."""
        from mcp_server.endpoints import EndpointResponse

        response = EndpointResponse(success=True, data={"key": "value"})
        result = response.to_dict()
        assert result["success"] is True
        assert result["data"]["key"] == "value"

    def test_error_response(self):
        """Test error response creation."""
        from mcp_server.endpoints import EndpointResponse

        response = EndpointResponse(success=False, error="Test error")
        result = response.to_dict()
        assert result["success"] is False
        assert result["error"] == "Test error"

    def test_response_with_metadata(self):
        """Test response with metadata."""
        from mcp_server.endpoints import EndpointResponse

        response = EndpointResponse(
            success=True, data={"key": "value"}, metadata={"version": "0.1.0"}
        )
        result = response.to_dict()
        assert result["metadata"]["version"] == "0.1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
