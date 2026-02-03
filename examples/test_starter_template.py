"""
MoltLang Inter-Model Communication Test Starter

Copy this file to create test scenarios for different model pairs.
Replace the placeholders with your specific test configuration.
"""

# =============================================================================
# CONFIGURATION - Edit this section
# =============================================================================

MY_MODEL_NAME = "claude-opus"  # Your model identifier
PARTNER_MODEL_NAME = "claude-haiku"  # Who you're testing with
TEST_ID = "test-001"  # Which test scenario

# Test scenarios (pick one or create custom)
TEST_SCENARIOS = {
    "test-001": {
        "initial_message": "Fetch user data from the API and return JSON",
        "expected_molt": "[OP:FETCH][SRC:API][RET:JSON]",
        "description": "Basic API fetch operation"
    },
    "test-002": {
        "initial_message": "Parse JSON data from file, validate structure, transform to CSV",
        "expected_molt": "[OP:PARSE][SRC:FILE][RET:JSON][OP:VALIDATE][OP:TRANSFORM][RET:text]",
        "description": "Complex data pipeline"
    },
    "test-003": {
        "initial_message": "Search database for user with ID 12345, return profile as dictionary",
        "expected_molt": "[OP:SEARCH][SRC:DB][PARAM:key=12345][RET:dict]",
        "description": "Parameter passing"
    },
}

# =============================================================================
# IMPORTS
# =============================================================================

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from moltlang import translate_to_molt, translate_from_molt, validate_translation
from tests.inter_model_communication import (
    HandoffFile,
    HandoffStatus,
    MessageType,
    get_handoff_file,
    send_message,
    log_issue,
    wait_for_turn,
)

# =============================================================================
# TEST FUNCTIONS
# =============================================================================


def initialize_test(test_id: str = TEST_ID) -> None:
    """
    Initialize a new test conversation.

    Call this if you're the initiator (Model A).
    """
    print(f"🚀 Initializing {test_id}...")

    # Load or create handoff file
    handoff_path = get_handoff_file()
    if handoff_path.exists():
        handoff = HandoffFile.load(handoff_path)
    else:
        handoff = HandoffFile()

    # Get test scenario
    scenario = TEST_SCENARIOS.get(test_id, {})
    if not scenario:
        print(f"❌ Unknown test ID: {test_id}")
        return

    # Create conversation
    conv = handoff.create_conversation(
        topic=scenario["description"],
        participant_a=MY_MODEL_NAME,
        participant_b=PARTNER_MODEL_NAME,
    )

    # Send initial instruction
    send_message(
        handoff,
        conv.id,
        sender=MY_MODEL_NAME,
        message_type=MessageType.INITIAL_INSTRUCTION,
        content=scenario["initial_message"],
        metadata={
            "test_id": test_id,
            "expected_molt": scenario.get("expected_molt", ""),
        },
    )

    # Save handoff file
    handoff.save(handoff_path)

    print(f"✅ Test {test_id} initialized")
    print(f"   Topic: {scenario['description']}")
    print(f"   Initial message: {scenario['initial_message']}")
    print(f"   ⏳ Waiting for {PARTNER_MODEL_NAME} to respond...")
    print(f"\n📍 Handoff file: {handoff_path}")


def respond_to_test() -> None:
    """
    Respond to a message from partner model.

    Call this if you're the responder (Model B).
    """
    print(f"📨 Checking for messages...")

    # Load handoff file
    handoff_path = get_handoff_file()
    if not handoff_path.exists():
        print(f"❌ No handoff file found at {handoff_path}")
        print("   Initialize a test first!")
        return

    handoff = HandoffFile.load(handoff_path)

    # Get active conversation
    conv = handoff.get_active_conversation()
    if not conv:
        print("❌ No active conversation found")
        return

    # Check if there's a message for us
    if not conv.has_unresponded_message(MY_MODEL_NAME):
        print(f"✅ No messages waiting for {MY_MODEL_NAME}")
        latest = conv.get_latest_message()
        if latest:
            print(f"   Latest from {latest.sender}: {latest.content}")
        return

    # Get the message
    msg = conv.get_latest_message()
    print(f"\n📥 Received from {msg.sender}:")
    print(f"   Content: {msg.content}")
    print(f"   Type: {msg.type.value}")

    # Process based on message type
    if msg.type == MessageType.INITIAL_INSTRUCTION:
        # Translate to MoltLang
        print(f"\n🔄 Translating to MoltLang...")
        molt_result = translate_to_molt(msg.content)
        molt_translation = molt_result.text

        print(f"   MoltLang: {molt_translation}")
        print(f"   Tokens: {molt_result.token_count}")
        print(f"   Efficiency: {molt_result.token_efficiency:.2%}")
        print(f"   Confidence: {molt_result.confidence:.2f}")

        # Send MoltLang response
        send_message(
            handoff,
            conv.id,
            sender=MY_MODEL_NAME,
            message_type=MessageType.MOLT_RESPONSE,
            content=molt_translation,
            metadata={
                "token_count": molt_result.token_count,
                "efficiency": molt_result.token_efficiency,
                "confidence": molt_result.confidence,
            },
        )

        # Log issues if any
        if molt_result.confidence < 0.8:
            log_issue(
                handoff,
                conv.id,
                MY_MODEL_NAME,
                "low_confidence",
                f"Translation confidence only {molt_result.confidence:.2f}",
                severity="warning",
            )

    elif msg.type == MessageType.MOLT_RESPONSE:
        # Validate and translate back
        print(f"\n🔄 Validating MoltLang and translating back...")

        # Translate back to English
        english_back = translate_from_molt(msg.content)
        print(f"   English: {english_back.text}")

        # Validate quality
        quality = validate_translation(
            msg.metadata.get("original_text", ""),
            msg.content,
        )

        print(f"   Valid: {quality.is_valid}")
        print(f"   Score: {quality.score:.2f}")
        print(f"   Efficiency: {quality.token_efficiency:.2%}")

        # Send validation result
        send_message(
            handoff,
            conv.id,
            sender=MY_MODEL_NAME,
            message_type=MessageType.VALIDATION_RESULT,
            content=f"Validation complete. Score: {quality.score:.2f}",
            metadata={
                "is_valid": quality.is_valid,
                "efficiency": quality.token_efficiency,
                "issues": len(quality.issues),
            },
        )

        # Mark conversation complete
        conv.status = HandoffStatus.COMPLETED

    else:
        print(f"⚠️  Unknown message type: {msg.type}")

    # Save handoff file
    handoff.save(handoff_path)
    print(f"\n✅ Response sent!")


def check_status() -> None:
    """Check the current status of all conversations."""
    handoff_path = get_handoff_file()
    if not handoff_path.exists():
        print("❌ No handoff file found")
        return

    handoff = HandoffFile.load(handoff_path)

    print(f"\n📊 MoltLang Test Session Status")
    print(f"=" * 50)
    print(f"Session ID: {handoff.session_id}")
    print(f"Status: {handoff.status.value}")
    print(f"Total conversations: {len(handoff.conversations)}")
    print(f"Active: {handoff.active_conversation_id}")

    for conv in handoff.conversations:
        print(f"\n💬 {conv.id}: {conv.topic}")
        print(f"   Status: {conv.status.value}")
        print(f"   Participants: {conv.participant_a} ↔ {conv.participant_b}")
        print(f"   Messages: {len(conv.messages)}")

        if conv.messages:
            latest = conv.messages[-1]
            print(f"   Latest: {latest.sender} - {latest.content[:50]}...")

        metrics = conv.get_efficiency_metrics()
        if metrics:
            print(f"   Metrics: {metrics}")


def wait_and_respond(timeout: int = 300) -> None:
    """
    Wait for partner's message and respond.

    This blocks until a message is received or timeout.
    """
    handoff_path = get_handoff_file()
    if not handoff_path.exists():
        print("❌ No handoff file found")
        return

    handoff = HandoffFile.load(handoff_path)

    print(f"⏳ Waiting for message from {PARTNER_MODEL_NAME}...")
    print(f"   Timeout: {timeout} seconds")
    print(f"   Polling every 2 seconds...")

    if wait_for_turn(handoff, MY_MODEL_NAME, timeout):
        print(f"✅ Message received!")
        respond_to_test()
    else:
        print(f"⏰ Timeout reached - no message received")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main():
    """Main entry point for running tests."""
    import argparse

    parser = argparse.ArgumentParser(description="MoltLang Inter-Model Test Runner")
    parser.add_argument(
        "action",
        choices=["init", "respond", "status", "wait"],
        help="Action to perform",
    )
    parser.add_argument("--test", default=TEST_ID, help="Test ID to run")

    args = parser.parse_args()

    if args.action == "init":
        initialize_test(args.test)
    elif args.action == "respond":
        respond_to_test()
    elif args.action == "status":
        check_status()
    elif args.action == "wait":
        wait_and_respond()


if __name__ == "__main__":
    # For interactive use in Claude Code:
    # You can call these functions directly instead of using argparse

    print("🤖 MoltLang Inter-Model Test Runner")
    print("=" * 50)
    print(f"My Model: {MY_MODEL_NAME}")
    print(f"Partner: {PARTNER_MODEL_NAME}")
    print(f"Test: {TEST_ID}")
    print("\nAvailable functions:")
    print("  - initialize_test()    # Start a new test")
    print("  - respond_to_test()    # Respond to a message")
    print("  - check_status()       # Show all conversations")
    print("  - wait_and_respond()   # Wait for message then respond")
    print("\nOr run with:")
    print("  python examples/test_starter_template.py init")
    print("  python examples/test_starter_template.py respond")
    print("  python examples/test_starter_template.py status")
    print("=" * 50)
