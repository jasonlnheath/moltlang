"""
MoltLang MCP API endpoints.

This module provides the HTTP/WebSocket endpoints for the MoltLang MCP server.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class EndpointType(Enum):
    """Types of MCP endpoints."""

    TRANSLATE = "translate"
    VALIDATE = "validate"
    VOCABULARY = "vocabulary"
    HEALTH = "health"


@dataclass
class EndpointResponse:
    """
    Response from an MCP endpoint.

    Attributes:
        success: Whether the request was successful
        data: Response data
        error: Error message if unsuccessful
        metadata: Optional metadata about the response
    """

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.error is not None:
            result["error"] = self.error
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result


class MCPEndpoints:
    """
    MoltLang MCP endpoints.

    Provides HTTP/WebSocket endpoints for MoltLang translation services.
    """

    def __init__(self):
        """Initialize the MCP endpoints."""
        from moltlang import MoltTranslator, MoltValidator

        self.translator = MoltTranslator()
        self.validator = MoltValidator()

    async def translate(
        self, text: str, to_molt: bool = True, target_language: str = "en"
    ) -> EndpointResponse:
        """
        Translate between human language and MoltLang.

        Args:
            text: Text to translate
            to_molt: True for human -> MoltLang, False for MoltLang -> human
            target_language: Target language code

        Returns:
            EndpointResponse with translation result
        """
        try:
            if to_molt:
                result = self.translator.translate_to_molt(text)
                data = {
                    "moltlang": result.text,
                    "token_count": result.token_count,
                    "original_token_count": result.original_token_count,
                    "efficiency": result.token_efficiency,
                    "confidence": result.confidence,
                }
            else:
                result = self.translator.translate_from_molt(text)
                data = {
                    "translation": result.text,
                    "token_count": result.token_count,
                    "confidence": result.confidence,
                }

            return EndpointResponse(success=True, data=data)
        except Exception as e:
            return EndpointResponse(success=False, error=str(e))

    async def validate(self, original: str, translated: str) -> EndpointResponse:
        """
        Validate a translation.

        Args:
            original: Original text
            translated: Translated text

        Returns:
            EndpointResponse with validation result
        """
        try:
            quality = self.validator.validate_translation(original, translated)
            data = {
                "is_valid": quality.is_valid,
                "score": quality.score,
                "token_efficiency": quality.token_efficiency,
                "confidence": quality.confidence,
                "issues": [
                    {
                        "type": issue.type.value,
                        "message": issue.message,
                        "severity": issue.severity,
                    }
                    for issue in quality.issues
                ],
                "metrics": quality.metrics,
            }
            return EndpointResponse(success=True, data=data)
        except Exception as e:
            return EndpointResponse(success=False, error=str(e))

    async def vocabulary(self, token_type: str | None = None) -> EndpointResponse:
        """
        List MoltLang vocabulary/tokens.

        Args:
            token_type: Optional token type filter

        Returns:
            EndpointResponse with token list
        """
        try:
            from moltlang.tokens import TokenType, TokenRegistry

            registry = TokenRegistry()

            if token_type:
                token_type_prefix = token_type.upper()
                tokens = [t for t in TokenType if t.name.startswith(token_type_prefix)]
            else:
                tokens = list(TokenType)

            data = {
                "tokens": [{"name": t.name, "value": t.value} for t in tokens],
                "count": len(tokens),
                "filtered_by": token_type,
            }
            return EndpointResponse(success=True, data=data)
        except Exception as e:
            return EndpointResponse(success=False, error=str(e))

    async def health(self) -> EndpointResponse:
        """
        Health check endpoint.

        Returns:
            EndpointResponse with health status
        """
        data = {
            "status": "healthy",
            "version": "0.1.0",
            "services": {
                "translator": "ok",
                "validator": "ok",
            },
        }
        return EndpointResponse(success=True, data=data)
