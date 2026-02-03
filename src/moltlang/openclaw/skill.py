"""
MoltLang OpenClaw Skill.

This module implements the OpenClaw skill for MoltLang translation.
"""

from typing import Any

from moltlang import translate_to_molt, translate_from_molt, MoltTranslator


class MoltLangOpenClawSkill:
    """
    OpenClaw skill for MoltLang translation.

    Enables OpenClaw agents to use MoltLang for efficient communication.
    """

    def __init__(self):
        """Initialize the skill."""
        self.name = "moltlang"
        self.version = "0.1.0"
        self.description = "Translate between human language and MoltLang"
        self.translator = MoltTranslator()

    async def handle_message(self, message: str, context: dict[str, Any]) -> str:
        """
        Handle incoming messages and translate to MoltLang.

        Args:
            message: Human language message
            context: OpenClaw context

        Returns:
            MoltLang translation
        """
        return self.translator.translate_to_molt(message).text

    async def handle_molt_message(self, molt: str, context: dict[str, Any]) -> str:
        """
        Handle MoltLang messages and translate to human language.

        Args:
            molt: MoltLang message
            context: OpenClaw context

        Returns:
            Human language translation
        """
        return self.translator.translate_from_molt(molt).text

    def get_commands(self) -> list[dict[str, Any]]:
        """Return available commands for OpenClaw."""
        return [
            {
                "name": "molt",
                "description": "Translate text to MoltLang",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate",
                        "required": True,
                    }
                },
            },
            {
                "name": "unmolt",
                "description": "Translate MoltLang to human language",
                "parameters": {
                    "molt": {
                        "type": "string",
                        "description": "MoltLang text",
                        "required": True,
                    }
                },
            },
        ]
