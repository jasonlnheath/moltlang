"""
MoltLang OpenClaw Integration Demo.

This file demonstrates how to integrate MoltLang with OpenClaw
for AI agent communication.
"""

# This is a placeholder for OpenClaw integration
# Actual implementation will require OpenClaw SDK

from moltlang import translate_to_molt, translate_from_molt


class MoltLangOpenClawSkill:
    """
    OpenClaw skill for MoltLang translation.

    This skill enables OpenClaw agents to:
    1. Translate human messages to MoltLang
    2. Translate MoltLang messages to human language
    3. Use MoltLang for efficient agent-to-agent communication
    """

    def __init__(self):
        """Initialize the MoltLang skill."""
        self.name = "moltlang"
        self.version = "0.1.0"
        self.description = "Translate between human language and MoltLang"

    async def handle_message(self, message: str, context: dict) -> str:
        """
        Handle incoming messages and translate to MoltLang.

        Args:
            message: Human language message
            context: OpenClaw context

        Returns:
            MoltLang translation
        """
        molt = translate_to_molt(message)
        return molt

    async def handle_molt_message(self, molt: str, context: dict) -> str:
        """
        Handle MoltLang messages and translate to human language.

        Args:
            molt: MoltLang message
            context: OpenClaw context

        Returns:
            Human language translation
        """
        human = translate_from_molt(molt)
        return human

    def get_commands(self) -> list[dict]:
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


def demo_openclaw_skill():
    """Demonstrate the OpenClaw skill usage."""
    print("=" * 50)
    print("OpenClaw Skill Demo")
    print("=" * 50)

    skill = MoltLangOpenClawSkill()

    # Example 1: Human message to MoltLang
    human_msg = "Fetch user profile from database"
    molt_result = await skill.handle_message(human_msg, {})
    print(f"Human: {human_msg}")
    print(f"MoltLang: {molt_result}")
    print()

    # Example 2: MoltLang to human
    molt_msg = "[OP:FETCH][SRC:DB][RET:JSON]"
    human_result = await skill.handle_molt_message(molt_msg, {})
    print(f"MoltLang: {molt_msg}")
    print(f"Human: {human_result}")
    print()

    # Example 3: Available commands
    commands = skill.get_commands()
    print("Available commands:")
    for cmd in commands:
        print(f"  - {cmd['name']}: {cmd['description']}")
    print()


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo_openclaw_skill())
