# Option 3: Webhook + Helper Bot for Moltbook - Implementation Plan

## Overview

Create a system that monitors Moltbook posts for new comments, uses AI to draft responses, and posts back with human oversight/approval.

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│  Moltbook   │────▶│  Webhook     │────▶│  Response   │────▶│  Approval   │
│  Platform   │     │  Receiver    │     │  Generator  │     │  Queue      │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
                            │                                      │
                            ▼                                      ▼
                     ┌──────────────┐                      ┌─────────────┐
                     │  Comment     │                      │  Human      │
                     │  Store       │                      │  Review     │
                     └──────────────┘                      └─────────────┘
```

---

## Components Needed

### 1. Moltbook Webhook Receiver
**Purpose:** Receive notifications when comments are posted

**Research Needed:**
- Does Moltbook have webhook support?
- What events trigger webhooks?
- Authentication method?
- Rate limits?

**Tech Options:**
- Express.js server (if webhooks exist)
- Polling fallback (if no webhooks)
- Serverless function (AWS Lambda, Railway, etc.)

### 2. Comment Store
**Purpose:** Track processed comments, avoid duplicates

**Tech Options:**
- SQLite (simple, local)
- PostgreSQL (production)
- Redis (fast, temporary)
- JSON file (simplest, not production)

**Schema:**
```sql
CREATE TABLE comments (
  id TEXT PRIMARY KEY,
  post_id TEXT,
  author TEXT,
  content TEXT,
  received_at TIMESTAMP,
  status TEXT,  -- pending, approved, rejected, posted
  response_text TEXT
);
```

### 3. Response Generator (AI)
**Purpose:** Draft contextual responses to comments

**Tech Options:**
- OpenAI API (`gpt-4`, `gpt-4-turbo`)
- Anthropic API (`claude-3-opus`)
- Local model (Ollama, llama.cpp)

**Prompt Template:**
```
You are MoltLang community manager. A user commented on our recruitment post.

Comment: "{comment_content}"
Author: "{comment_author}"
Context: {previous_comments}

Draft a helpful, friendly response that:
1. Answers their question
2. Encourages trying MoltLang
3. Provides relevant example
4. Stays under 200 words
```

### 4. Approval Queue / Human Review
**Purpose:** Human oversight before posting

**Tech Options:**
- Web dashboard (simple UI)
- Discord/Slack bot (notifications + quick approve/reject)
- CLI tool (for developers)
- GitHub Issues (track as issues)

**UI Options:**
- Simple HTML page
- Streamlit (Python)
- Gradio (Python)
- Custom React app

### 5. Moltbook Poster
**Purpose:** Post approved responses back to Moltbook

**Research Needed:**
- Moltbook API for posting comments
- Authentication (API token?)
- Rate limits
- Formatting (markdown support?)

---

## Tech Stack Recommendation

### Minimal Viable Product (MVP)

```
┌─────────────────────────────────────────────────────────────┐
│  Technology Stack                                           │
├─────────────────────────────────────────────────────────────┤
│  Backend:    Node.js + Express                              │
│  Database:   SQLite (docker volume)                         │
│  AI:         OpenAI API (gpt-4-turbo)                       │
│  Hosting:   Railway (same as moltlang MCP server)           │
│  Frontend:   Simple HTML dashboard                          │
│  Notifications: npx команда for approvals (CLI initially)    │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### Phase 1: Research (1-2 hours)
- [ ] Check if Moltbook has webhook/API documentation
- [ ] Test Moltbook API endpoints
- [ ] Document authentication method
- [ ] Identify rate limits

### Phase 2: Webhook Receiver (2-4 hours)
- [ ] Set up Express server
- [ ] Implement webhook endpoint
- [ ] Add comment storage
- [ ] Test with sample data

### Phase 3: Response Generator (2-3 hours)
- [ ] Set up OpenAI/Anthropic API
- [ ] Create prompt templates
- [ ] Implement generation logic
- [ ] Add context tracking

### Phase 4: Approval System (3-5 hours)
- [ ] Create simple approval UI
- [ ] Add approve/reject buttons
- [ ] Implement edit capability
- [ ] Add response history

### Phase 5: Moltbook Poster (2-4 hours)
- [ ] Implement Moltbook API client
- [ ] Add posting logic
- [ ] Test with draft comments
- [ ] Add error handling

### Phase 6: Integration & Testing (2-3 hours)
- [ ] End-to-end testing
- [ ] Error handling
- [ ] Monitoring/logging
- [ ] Deployment

---

## Estimated Effort

| Phase | Time | Complexity |
|-------|------|------------|
| Research | 1-2 hours | Medium |
| Webhook Receiver | 2-4 hours | Low |
| Response Generator | 2-3 hours | Low |
| Approval System | 3-5 hours | Medium |
| Moltbook Poster | 2-4 hours | Medium (depends on API) |
| Integration | 2-3 hours | Medium |
| **Total** | **12-21 hours** | |

---

## Key Unknowns (Research Required)

### 1. Moltbook Webhook/API
- **Critical:** Does Moltbook have webhooks?
- **Critical:** How to authenticate API requests?
- **Important:** What are the rate limits?
- **Important:** Comment posting API format?

### 2. Moderation
- **Important:** How to handle spam/inappropriate comments?
- **Important:** How to detect and handle abuse?

### 3. Costs
- OpenAI API: ~$0.01-0.03 per response
- Hosting: Free on Railway (within limits)
- Total: ~$10-50/month depending on volume

---

## Safety & Trust Considerations

### Risks
- AI generates inappropriate responses
- Bot posts without approval (bug)
- Account compromised
- Spam amplification

### Mitigations
- **Mandatory human approval** before posting
- **Response review dashboard**
- **Rate limiting** on posts
- **Audit logging** of all actions
- **Emergency stop** button
- **Content filtering** on generated responses

---

## Alternative: Simpler Approach

If webhooks aren't available or this is too complex:

### Polling-Based Approach
```
Every 5 minutes:
1. Check Moltbook for new comments
2. Generate responses for new ones
3. Store in approval queue
4. Notify human (email/Discord)
```

**Simpler but:** not truly instant, uses API quota

---

## Next Steps

1. **Research Moltbook API** - Check documentation for webhooks/comment API
2. **Test API endpoints** - Verify authentication works
3. **Build MVP** - Start with polling, add webhooks if available
4. **Deploy & test** - Start with one post, monitor, expand

---

## Decision Point

**Proceed with Option 3?**

- If Moltbook has good API/webhook support → **Yes, build it**
- If Moltbook has no API → **No, use Option 1 (manual) instead**
- If unsure → **Research first (2 hours) before deciding**

---

*Created: 2026-02-04*
*Status: Planning - Research needed*
