# MoltLang Inter-Model Testing Guide

## Overview

This guide explains how to test MoltLang communication between different AI models using the file-based handoff system.

## Setup

1. **Locate the handoff file:** `C:/dev/moltlang/moltlang_handoff.json`

2. **Identify your model:**
   - `claude-opus`
   - `claude-sonnet`
   - `claude-haiku`
   - `glm-4.5-air`
   - Other model name

## How It Works

```
┌─────────────────┐                    ┌─────────────────┐
│  Model A (Opus) │                    │ Model B (Haiku) │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │  1. Read handoff file                │
         │  2. Check for messages               │
         │  3. Process message                  │
         │  4. Write response                   │
         │                                      │
         └──────────────┬───────────────────────┘
                        │
                        ▼
              ┌───────────────────┐
              │  Handoff File     │
              │  (JSON)           │
              └───────────────────┘
```

## Test Scenarios

We have **8 test scenarios** to validate core functionality:

### Test 001: Basic API Fetch
**Goal:** Test simple operation translation
**Initial:** "Fetch user data from the API and return JSON"
**Expected:** `[OP:FETCH][SRC:API][RET:JSON]`

### Test 002: Complex Data Pipeline
**Goal:** Test multi-step operations
**Initial:** "Parse JSON data from file, validate structure, transform to CSV"
**Expected:** `[OP:PARSE][SRC:FILE][RET:JSON][OP:VALIDATE][OP:TRANSFORM][RET:text]`

### Test 003: Database Query with Parameters
**Goal:** Test parameter passing
**Initial:** "Search database for user with ID 12345, return profile as dictionary"
**Expected:** `[OP:SEARCH][SRC:DB][PARAM:key=12345][RET:dict]`

### Test 004: Roundtrip Translation
**Goal:** Test meaning preservation
**Process:** English → MoltLang → English
**Criteria:** Key semantics preserved, confidence > 0.8

### Test 005: Cross-Model Understanding
**Goal:** Test if Model B understands Model A's MoltLang
**Initial:** "Compute aggregate statistics from cached data, return numeric result"
**Criteria:** Model B correctly translates back

### Test 006: Error Handling
**Goal:** Test control flow and error tokens
**Initial:** "Try to fetch from API, retry on failure, otherwise log error"
**Expected:** `[CTL:TRY][OP:FETCH][SRC:API][CTL:CATCH][ERR:RETRY][ERR:LOG]`

### Test 007: Async Operation
**Goal:** Test modifier tokens
**Initial:** "Asynchronously fetch from multiple APIs in parallel, aggregate results"
**Expected:** `[MOD:ASYNC][MOD:PARALLEL][OP:FETCH][SRC:API][OP:AGGREGATE]`

### Test 008: Type System
**Goal:** Test data type tokens
**Initial:** "Parse data and ensure it returns a properly typed list of strings"
**Expected:** `[OP:PARSE][RET:list][TYPE:str]`

## Step-by-Step Instructions

### For Model A (Initiator)

1. **Initialize the test:**
```python
from tests.inter_model_communication import (
    HandoffFile, HandoffStatus, MessageType,
    get_handoff_file, send_message
)

# Load or create handoff file
handoff = HandoffFile.load(get_handoff_file())

# Create conversation for test
conv = handoff.create_conversation(
    topic="Basic API Fetch",
    participant_a="claude-opus",  # Your name
    participant_b="claude-haiku",  # Partner model
)

# Send initial instruction
send_message(
    handoff,
    conv.id,
    sender="claude-opus",
    message_type=MessageType.INITIAL_INSTRUCTION,
    content="Fetch user data from the API and return JSON",
    metadata={"test_id": "test-001"}
)

# Save handoff file
handoff.save(get_handoff_file())
print("Message sent! Waiting for Model B to respond...")
```

### For Model B (Responder)

1. **Wait for message:**
```python
from tests.inter_model_communication import (
    HandoffFile, MessageType,
    get_handoff_file, send_message, log_issue
)

# Load handoff file
handoff = HandoffFile.load(get_handoff_file())

# Get active conversation
conv = handoff.get_active_conversation()
if not conv:
    print("No active conversation found")
    exit()

# Get latest message
msg = conv.get_latest_message()
print(f"Received from {msg.sender}: {msg.content}")

# Translate to MoltLang
from moltlang import translate_to_molt
molt_result = translate_to_molt(msg.content)
molt_translation = molt_result.text

# Send MoltLang response
send_message(
    handoff,
    conv.id,
    sender="claude-haiku",
    message_type=MessageType.MOLT_RESPONSE,
    content=molt_translation,
    metadata={
        "token_count": molt_result.token_count,
        "efficiency": molt_result.token_efficiency,
        "confidence": molt_result.confidence
    }
)

# Log any issues
if molt_result.confidence < 0.8:
    log_issue(
        handoff,
        conv.id,
        "claude-haiku",
        "low_confidence",
        f"Translation confidence only {molt_result.confidence:.2f}",
        severity="warning"
    )

# Save handoff file
handoff.save(get_handoff_file())
```

### For Model A (Validation)

1. **Validate the response:**
```python
from tests.inter_model_communication import (
    HandoffFile, MessageType,
    get_handoff_file, send_message
)
from moltlang import translate_from_molt, validate_translation

# Load handoff file
handoff = HandoffFile.load(get_handoff_file())
conv = handoff.get_active_conversation()

# Get MoltLang response
molt_msg = conv.get_latest_message()
print(f"MoltLang: {molt_msg.content}")

# Translate back to English
english_back = translate_from_molt(molt_msg.content)
print(f"English: {english_back.text}")

# Validate quality
quality = validate_translation(
    "Fetch user data from the API and return JSON",
    molt_msg.content
)

send_message(
    handoff,
    conv.id,
    sender="claude-opus",
    message_type=MessageType.VALIDATION_RESULT,
    content=f"Roundtrip complete. Score: {quality.score:.2f}",
    metadata={
        "is_valid": quality.is_valid,
        "efficiency": quality.token_efficiency,
        "issues": len(quality.issues)
    }
)

# Mark conversation as complete
conv.status = HandoffStatus.COMPLETED
handoff.save(get_handoff_file())

print("Test complete!")
```

## Logging Issues

Models should log issues when:

| Issue Type | When to Log | Example |
|------------|-------------|---------|
| `translation_error` | MoltLang has wrong tokens | Missing operation token |
| `low_confidence` | Confidence < 0.8 | Ambiguous instruction |
| `roundtrip_loss` | Meaning lost in roundtrip | "API" became "file" |
| `parameter_loss` | Parameter value dropped | ID value missing |
| `syntax_error` | Invalid MoltLang syntax | Mismatched brackets |
| `efficiency_warning` | Efficiency < 50% | Not enough reduction |

## Test Execution Matrix

| Test | Opus → Haiku | Sonnet → Haiku | Opus → GLM | Haiku → Opus |
|------|--------------|----------------|------------|-------------|
| 001: Basic API | ✓ | ✓ | ✓ | ✓ |
| 002: Pipeline | ✓ | ✓ | ✓ | ✓ |
| 003: Parameters | ✓ | ✓ | ✓ | ✓ |
| 004: Roundtrip | ✓ | ✓ | ✓ | ✓ |
| 005: Cross-Model | ✓ | ✓ | ✓ | ✓ |
| 006: Error Handling | ✓ | ✓ | ✓ | ✓ |
| 007: Async | ✓ | ✓ | ✓ | ✓ |
| 008: Types | ✓ | ✓ | ✓ | ✓ |

## Running Tests

### Sequential (One Conversation at a Time)

```
Session 1 (Opus):  Initialize Test 001
Session 2 (Haiku): Respond with MoltLang
Session 1 (Opus):  Validate and complete
```

### Parallel (Multiple Conversations)

The handoff file supports multiple concurrent conversations. Each conversation has:
- Unique ID
- Participant pair
- Independent message history

## Expected Results

### Success Criteria

1. **Token Efficiency:** > 50% reduction vs English
2. **Translation Accuracy:** > 95% confidence
3. **Roundtrip Preservation:** > 90% semantic similarity
4. **Cross-Model Understanding:** Partner model correctly interprets

### Failure Indicators

- Missing required tokens (OP, SRC)
- Wrong token type (FILE instead of API)
- Parameter values dropped
- Control flow broken
- Low confidence scores

## Report Generation

After testing, generate a report:

```python
from tests.inter_model_communication import generate_test_report, HandoffFile, get_handoff_file

handoff = HandoffFile.load(get_handoff_file())
report = generate_test_report(handoff)

import json
print(json.dumps(report, indent=2))
```

## Quick Start Example

**In your Claude Code session (Opus):**

```
Read C:/dev/moltlang/moltlang_handoff.json
Create conversation for test-001 with participant_b="claude-haiku"
Send initial instruction: "Fetch user data from the API and return JSON"
Save file
```

**In another session (Haiku):**

```
Read C:/dev/moltlang/moltlang_handoff.json
Find active conversation
Read message from claude-opus
Translate to MoltLang using moltlang.translate_to_molt()
Send MoltLang response
Save file
```

## Next Steps

1. Start with Test 001 (simplest)
2. Progress through Tests 002-008
3. Document all issues in handoff file
4. Generate final report
5. Analyze patterns in failures
