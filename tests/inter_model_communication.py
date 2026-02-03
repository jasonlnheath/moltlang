"""
MoltLang Inter-Model Communication Test Framework

This module provides a framework for testing MoltLang communication
between different AI models (Opus, Sonnet, Haiku, GLM, etc.).

The framework uses a file-based handoff system where models:
1. Read the handoff file for incoming messages
2. Process the message (translate to/from MoltLang)
3. Write their response back to the file
4. Log any issues/gaps encountered
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class HandoffStatus(Enum):
    """Status of the handoff process."""

    READY = "ready"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_RESPONSE = "waiting_for_response"
    COMPLETED = "completed"
    ERROR = "error"


class MessageType(Enum):
    """Types of messages in the conversation."""

    INITIAL_INSTRUCTION = "initial_instruction"
    MOLT_RESPONSE = "molt_response"
    HUMAN_TRANSLATION = "human_translation"
    VALIDATION_RESULT = "validation_result"
    ISSUE_REPORT = "issue_report"
    STATUS_UPDATE = "status_update"


@dataclass
class Message:
    """A message in the conversation."""

    id: str
    type: MessageType
    sender: str  # Model name (e.g., "claude-opus", "claude-haiku")
    timestamp: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "content": self.content,
            "metadata": self.metadata,
            "issues": self.issues,
        }


@dataclass
class Conversation:
    """A conversation between two models."""

    id: str
    topic: str
    status: HandoffStatus
    participant_a: str
    participant_b: str
    messages: list[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "topic": self.topic,
            "status": self.status.value,
            "participant_a": self.participant_a,
            "participant_b": self.participant_b,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def get_latest_message(self) -> Message | None:
        """Get the most recent message."""
        return self.messages[-1] if self.messages else None

    def has_unresponded_message(self, sender: str) -> bool:
        """Check if there's a message from another sender waiting for response."""
        latest = self.get_latest_message()
        return latest and latest.sender != sender

    def get_efficiency_metrics(self) -> dict[str, Any]:
        """Calculate efficiency metrics for the conversation."""
        if not self.messages:
            return {}

        # Count message types
        molt_messages = [m for m in self.messages if m.type == MessageType.MOLT_RESPONSE]
        issues = sum(len(m.issues) for m in self.messages)

        # Calculate average response time (if timestamps allow)
        response_times = []
        for i in range(1, len(self.messages)):
            try:
                prev_time = datetime.fromisoformat(self.messages[i - 1].timestamp)
                curr_time = datetime.fromisoformat(self.messages[i].timestamp)
                response_times.append((curr_time - prev_time).total_seconds())
            except:
                pass

        return {
            "total_messages": len(self.messages),
            "molt_messages": len(molt_messages),
            "total_issues": issues,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
        }


@dataclass
class HandoffFile:
    """The handoff file structure."""

    version: str = "0.1.0"
    session_id: str = "test-001"
    status: HandoffStatus = HandoffStatus.READY
    conversations: list[Conversation] = field(default_factory=list)
    active_conversation_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "session_id": self.session_id,
            "status": self.status.value,
            "conversations": [c.to_dict() for c in self.conversations],
            "active_conversation_id": self.active_conversation_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    def save(self, filepath: Path) -> None:
        """Save to file."""
        self.updated_at = datetime.utcnow().isoformat()
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> "HandoffFile":
        """Load from file."""
        with open(filepath) as f:
            data = json.load(f)

        handoff = cls()
        handoff.version = data.get("version", "0.1.0")
        handoff.session_id = data.get("session_id", "test-001")
        handoff.status = HandoffStatus(data.get("status", "ready"))
        handoff.active_conversation_id = data.get("active_conversation_id")
        handoff.created_at = data.get("created_at", datetime.utcnow().isoformat())
        handoff.updated_at = data.get("updated_at", datetime.utcnow().isoformat())
        handoff.metadata = data.get("metadata", {})

        # Load conversations
        for conv_data in data.get("conversations", []):
            conv = Conversation(
                id=conv_data["id"],
                topic=conv_data["topic"],
                status=HandoffStatus(conv_data["status"]),
                participant_a=conv_data["participant_a"],
                participant_b=conv_data["participant_b"],
                created_at=conv_data.get("created_at", datetime.utcnow().isoformat()),
                updated_at=conv_data.get("updated_at", datetime.utcnow().isoformat()),
            )
            for msg_data in conv_data.get("messages", []):
                msg = Message(
                    id=msg_data["id"],
                    type=MessageType(msg_data["type"]),
                    sender=msg_data["sender"],
                    timestamp=msg_data["timestamp"],
                    content=msg_data["content"],
                    metadata=msg_data.get("metadata", {}),
                    issues=msg_data.get("issues", []),
                )
                conv.messages.append(msg)
            handoff.conversations.append(conv)

        return handoff

    def create_conversation(
        self,
        topic: str,
        participant_a: str,
        participant_b: str,
    ) -> Conversation:
        """Create a new conversation."""
        conv = Conversation(
            id=f"conv-{len(self.conversations) + 1}",
            topic=topic,
            status=HandoffStatus.READY,
            participant_a=participant_a,
            participant_b=participant_b,
        )
        self.conversations.append(conv)
        self.active_conversation_id = conv.id
        return conv

    def get_active_conversation(self) -> Conversation | None:
        """Get the active conversation."""
        if not self.active_conversation_id:
            return None
        for conv in self.conversations:
            if conv.id == self.active_conversation_id:
                return conv
        return None

    def get_conversation_by_participants(
        self, participant_a: str, participant_b: str
    ) -> Conversation | None:
        """Get conversation between two participants."""
        for conv in self.conversations:
            if (
                conv.participant_a == participant_a
                and conv.participant_b == participant_b
            ) or (
                conv.participant_a == participant_b
                and conv.participant_b == participant_a
            ):
                return conv
        return None


# Test scenarios for inter-model communication

TEST_SCENARIOS = [
    {
        "id": "test-001",
        "name": "Basic API Fetch",
        "description": "Test simple API operation translation",
        "initial_message": "Fetch user data from the API and return JSON",
        "expected_molt": "[OP:FETCH][SRC:API][RET:JSON]",
        "success_criteria": [
            "MoltLang contains correct operation token",
            "MoltLang contains correct source token",
            "MoltLang contains correct return type",
            "Token efficiency > 50%",
        ],
    },
    {
        "id": "test-002",
        "name": "Complex Data Pipeline",
        "description": "Test multi-step data processing",
        "initial_message": "Parse JSON data from file, validate the structure, then transform to CSV format",
        "expected_molt": "[OP:PARSE][SRC:FILE][RET:JSON][OP:VALIDATE][OP:TRANSFORM][RET:text]",
        "success_criteria": [
            "All operation tokens present",
            "Correct order maintained",
            "Token efficiency > 60%",
        ],
    },
    {
        "id": "test-003",
        "name": "Database Query with Parameters",
        "description": "Test parameter passing",
        "initial_message": "Search the database for user with ID 12345 and return their profile as a dictionary",
        "expected_molt": "[OP:SEARCH][SRC:DB][PARAM:key=12345][RET:dict]",
        "success_criteria": [
            "Parameter token present with value",
            "Correct return type",
            "Parameter value preserved",
        ],
    },
    {
        "id": "test-004",
        "name": "Roundtrip Translation",
        "description": "Test English → MoltLang → English preservation",
        "initial_message": "Validate input from the API endpoint",
        "success_criteria": [
            "Roundtrip preserves key semantics",
            "No significant meaning loss",
            "Confidence score > 0.8",
        ],
    },
    {
        "id": "test-005",
        "name": "Cross-Model Understanding",
        "description": "Test if Model B can understand Model A's MoltLang",
        "initial_message": "Compute aggregate statistics from cached data and return a numeric result",
        "success_criteria": [
            "Model B correctly translates back",
            "Key concepts preserved",
            "No misinterpretation",
        ],
    },
    {
        "id": "test-006",
        "name": "Error Handling",
        "description": "Test error handling tokens",
        "initial_message": "Try to fetch from the API, retry on failure, otherwise log the error",
        "expected_molt": "[CTL:TRY][OP:FETCH][SRC:API][CTL:CATCH][ERR:RETRY][ERR:LOG]",
        "success_criteria": [
            "Control flow tokens present",
            "Error handling tokens present",
            "Logical structure maintained",
        ],
    },
    {
        "id": "test-007",
        "name": "Async Operation",
        "description": "Test async/modifier tokens",
        "initial_message": "Asynchronously fetch data from multiple APIs in parallel and aggregate the results",
        "expected_molt": "[MOD:ASYNC][MOD:PARALLEL][OP:FETCH][SRC:API][OP:AGGREGATE]",
        "success_criteria": [
            "Modifier tokens present",
            "Parallel operation indicated",
            "Aggregation specified",
        ],
    },
    {
        "id": "test-008",
        "name": "Type System",
        "description": "Test data type tokens",
        "initial_message": "Parse the data and ensure it returns a properly typed list of strings",
        "expected_molt": "[OP:PARSE][RET:list][TYPE:str]",
        "success_criteria": [
            "Type token present",
            "Return type matches",
            "Type constraint understood",
        ],
    },
]


def generate_test_report(handoff: HandoffFile) -> dict[str, Any]:
    """Generate a comprehensive test report."""
    report = {
        "session_id": handoff.session_id,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_conversations": len(handoff.conversations),
            "completed": sum(1 for c in handoff.conversations if c.status == HandoffStatus.COMPLETED),
            "in_progress": sum(1 for c in handoff.conversations if c.status == HandoffStatus.IN_PROGRESS),
            "errors": sum(1 for c in handoff.conversations if c.status == HandoffStatus.ERROR),
        },
        "conversations": [],
        "issues": [],
        "recommendations": [],
    }

    for conv in handoff.conversations:
        conv_report = {
            "id": conv.id,
            "topic": conv.topic,
            "status": conv.status.value,
            "participants": [conv.participant_a, conv.participant_b],
            "metrics": conv.get_efficiency_metrics(),
            "issues": [],
            "success": False,
        }

        # Check for issues in messages
        for msg in conv.messages:
            for issue in msg.issues:
                conv_report["issues"].append({
                    "message_id": msg.id,
                    "sender": msg.sender,
                    "issue": issue,
                })
                report["issues"].append({
                    "conversation": conv.id,
                    "message_id": msg.id,
                    "sender": msg.sender,
                    "issue": issue,
                })

        # Determine success based on issues
        if conv.status == HandoffStatus.COMPLETED and len(conv_report["issues"]) == 0:
            conv_report["success"] = True

        report["conversations"].append(conv_report)

    # Generate recommendations
    total_issues = len(report["issues"])
    if total_issues > 5:
        report["recommendations"].append("High issue count detected - review token definitions")
    if any(c["metrics"].get("avg_response_time", 0) > 60 for c in report["conversations"]):
        report["recommendations"].append("Slow response times - consider optimizing translation logic")

    return report


# Convenience functions for model sessions

def get_handoff_file() -> Path:
    """Get the path to the handoff file."""
    return Path(__file__).parent.parent / "moltlang_handoff.json"


def wait_for_turn(handoff: HandoffFile, my_name: str, timeout: int = 300) -> bool:
    """
    Wait until it's this model's turn to respond.

    Args:
        handoff: The handoff file structure
        my_name: This model's identifier
        timeout: Maximum seconds to wait

    Returns:
        True if it's this model's turn, False if timeout
    """
    start = time.time()
    while time.time() - start < timeout:
        active = handoff.get_active_conversation()
        if active and active.has_unresponded_message(my_name):
            return True
        time.sleep(2)  # Poll every 2 seconds
    return False


def send_message(
    handoff: HandoffFile,
    conversation_id: str,
    sender: str,
    message_type: MessageType,
    content: str,
    metadata: dict[str, Any] | None = None,
    issues: list[dict[str, Any]] | None = None,
) -> None:
    """Send a message in a conversation."""
    conv = None
    for c in handoff.conversations:
        if c.id == conversation_id:
            conv = c
            break

    if not conv:
        raise ValueError(f"Conversation {conversation_id} not found")

    message = Message(
        id=f"msg-{len(conv.messages) + 1}",
        type=message_type,
        sender=sender,
        timestamp=datetime.utcnow().isoformat(),
        content=content,
        metadata=metadata or {},
        issues=issues or [],
    )

    conv.add_message(message)


def log_issue(
    handoff: HandoffFile,
    conversation_id: str,
    sender: str,
    issue_type: str,
    description: str,
    severity: str = "info",
) -> None:
    """Log an issue during communication."""
    conv = None
    for c in handoff.conversations:
        if c.id == conversation_id:
            conv = c
            break

    if not conv:
        return

    # Add to latest message from this sender
    for msg in reversed(conv.messages):
        if msg.sender == sender:
            msg.issues.append({
                "type": issue_type,
                "description": description,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
            })
            break
