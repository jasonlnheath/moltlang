"""
MoltLang MCP Integration Example.

This file demonstrates how to use the MoltLang MCP server
for AI agent integration.
"""

import asyncio
import json


async def example_translate_via_mcp():
    """Example: Translation via MCP endpoints."""
    print("=" * 50)
    print("Example: MCP Translation")
    print("=" * 50)

    from mcp_server.endpoints import MCPEndpoints

    endpoints = MCPEndpoints()

    # Translate to MoltLang
    response = await endpoints.translate("Fetch data from API", to_molt=True)
    print(f"Translation: {response.data['moltlang']}")
    print(f"Efficiency: {response.data['efficiency']:.2%}")
    print()


async def example_validate_via_mcp():
    """Example: Validation via MCP endpoints."""
    print("=" * 50)
    print("Example: MCP Validation")
    print("=" * 50)

    from mcp_server.endpoints import MCPEndpoints

    endpoints = MCPEndpoints()

    # Validate a translation
    response = await endpoints.validate(
        "Fetch data from API",
        "[OP:FETCH][SRC:API]",
    )

    print(f"Valid: {response.data['is_valid']}")
    print(f"Score: {response.data['score']:.2f}")
    print(f"Efficiency: {response.data['token_efficiency']:.2%}")
    print()


async def example_list_vocabulary():
    """Example: List vocabulary via MCP."""
    print("=" * 50)
    print("Example: MCP Vocabulary Listing")
    print("=" * 50)

    from mcp_server.endpoints import MCPEndpoints

    endpoints = MCPEndpoints()

    # List all tokens
    response = await endpoints.vocabulary()
    print(f"Total tokens: {response.data['count']}")

    # List only operation tokens
    op_response = await endpoints.vocabulary(token_type="OP")
    print(f"Operation tokens: {op_response.data['count']}")
    for token in op_response.data['tokens'][:5]:
        print(f"  - {token['name']}: {token['value']}")
    print()


async def example_health_check():
    """Example: MCP health check."""
    print("=" * 50)
    print("Example: MCP Health Check")
    print("=" * 50)

    from mcp_server.endpoints import MCPEndpoints

    endpoints = MCPEndpoints()
    response = await endpoints.health()

    print(f"Status: {response.data['status']}")
    print(f"Version: {response.data['version']}")
    print(f"Services: {response.data['services']}")
    print()


async def example_agent_workflow():
    """
    Example: Complete AI agent workflow using MCP.

    Demonstrates how an AI agent would use MoltLang for
    efficient communication.
    """
    print("=" * 50)
    print("Example: AI Agent Workflow")
    print("=" * 50)

    from mcp_server.endpoints import MCPEndpoints

    endpoints = MCPEndpoints()

    # Step 1: Agent receives human instruction
    human_instruction = "Fetch user data from the API and return JSON"
    print(f"Human instruction: {human_instruction}")

    # Step 2: Agent translates to MoltLang for internal processing
    molt_response = await endpoints.translate(human_instruction, to_molt=True)
    molt_code = molt_response.data['moltlang']
    print(f"MoltLang internal: {molt_code}")
    print(f"Token efficiency: {molt_response.data['efficiency']:.2%}")

    # Step 3: Agent validates the translation
    validation = await endpoints.validate(human_instruction, molt_code)
    print(f"Validation score: {validation.data['score']:.2f}")

    # Step 4: Agent shares MoltLang with another agent (efficient!)
    print(f"Agent-to-agent message: {molt_code}")

    # Step 5: Receiving agent translates back to human-readable
    human_response = await endpoints.translate(molt_code, to_molt=False)
    print(f"Reconstructed: {human_response.data['translation']}")
    print()


async def main():
    """Run all MCP examples."""
    print("\n" + "=" * 50)
    print("MoltLang MCP Integration Examples")
    print("=" * 50 + "\n")

    await example_translate_via_mcp()
    await example_validate_via_mcp()
    await example_list_vocabulary()
    await example_health_check()
    await example_agent_workflow()

    print("=" * 50)
    print("All MCP examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
