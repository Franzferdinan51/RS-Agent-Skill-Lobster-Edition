# 🦞 AGENT-FIRST Manifesto

**Why Agent-First Design Matters**

---

## 🎯 The Problem

Most CLI tools are designed for **humans**, not **agents**:

- ❌ Human-readable text output (hard to parse)
- ❌ No structured error handling
- ❌ No rate limiting (gets blocked)
- ❌ No session coordination
- ❌ No multi-agent workflows

---

## ✅ The Solution: Agent-First Design

### Principle 1: **JSON-First Output**

Every tool supports `--json` for structured, parseable output:

```bash
# Human-readable (fallback)
python3 tools/runescape-api.py --clan "Lords of Arcadia"

# Agent-ready (preferred)
python3 tools/runescape-api.py --clan "Lords of Arcadia" --json | jq '.total_members'
```

**Why it matters:**
- Agents can parse JSON reliably
- No regex or string parsing needed
- Schema is documented and stable
- Easy to chain tools together

---

### Principle 2: **Built-In Rate Limiting**

Every API call respects rate limits:

```python
# Default: 150ms between requests
api = RuneScapeAPI(rate_limit_ms=150)

# Slower for large clans
api = RuneScapeAPI(rate_limit_ms=300)
```

**Why it matters:**
- Prevents API bans
- Respectful to free public APIs
- Configurable per use case
- Agents don't need to implement their own

---

### Principle 3: **Structured Error Handling**

Errors return consistent JSON format:

```json
{
  "error": "Player not found",
  "player": "UnknownPlayer",
  "suggestion": "Check spelling or try OSRS hiscores"
}
```

**Why it matters:**
- Agents can handle errors programmatically
- No parsing error messages from text
- Consistent across all tools
- Includes suggestions for recovery

---

### Principle 4: **Session Coordination**

Tools work together via session coordination:

```python
# Spawn parallel agents
sessions_spawn(label="citadel-agent", task="Check caps")
sessions_spawn(label="inactive-agent", task="Find inactive members")
sessions_spawn(label="stats-agent", task="Calculate stats")

# Collect and aggregate results
results = collect_all()
generate_report(results)
```

**Why it matters:**
- Parallel processing (faster)
- Isolated agent contexts
- Easy to scale workflows
- Follows OpenClaw patterns

---

### Principle 5: **Composable Workflows**

Tools chain together naturally:

```bash
# Pipeline 1: Clan monitoring
python3 tools/runescape-api.py --clan "Lords" --json | \
  python3 tools/inactive-members.py --input - --json | \
  python3 scripts/send-alert.py

# Pipeline 2: Price tracking
python3 tools/runescape-api.py --item "Twisted bow" --json | \
  python3 tools/price-alert.py --threshold 300m --json | \
  python3 scripts/notify.py
```

**Why it matters:**
- Unix philosophy (do one thing well)
- Easy to create new workflows
- Agents can compose dynamically
- No monolithic scripts

---

## 🤖 Multi-Agent Patterns

### Pattern 1: **Fan-Out / Fan-In**

```python
# Fan-out: Spawn multiple agents
tasks = [
    ("agent-1", "Check clan caps"),
    ("agent-2", "Check inactive members"),
    ("agent-3", "Check clan stats")
]

for agent_id, task in tasks:
    sessions_spawn(label=agent_id, task=task)

# Fan-in: Collect all results
results = [collect_result(agent_id) for agent_id, _, _ in tasks]

# Aggregate
final_report = aggregate(results)
```

**Use case:** Parallel data collection

---

### Pattern 2: **Pipeline Processing**

```python
# Stage 1: Fetch data
data = fetch_clan_data("Lords of Arcadia")

# Stage 2: Process
processed = process_data(data)

# Stage 3: Analyze
analysis = analyze(processed)

# Stage 4: Report
report = generate_report(analysis)
```

**Use case:** Sequential data transformation

---

### Pattern 3: **Map-Reduce**

```python
# Map: Process each member
members = get_clan_members("Lords of Arcadia")
results = []
for member in members:
    result = check_member_activity(member)
    results.append(result)

# Reduce: Aggregate results
inactive = [r for r in results if r['inactive']]
active = [r for r in results if not r['inactive']]

report = {
    "total": len(members),
    "inactive": len(inactive),
    "active": len(active)
}
```

**Use case:** Processing large datasets

---

### Pattern 4: **Event-Driven**

```python
# Agent 1: Monitor for changes
while True:
    caps = check_citadel_caps()
    if caps['new_caps'] > 0:
        send_event("citadel_cap", caps)
    time.sleep(3600)

# Agent 2: Handle events
on_event("citadel_cap", lambda e: send_alert(e))
on_event("inactive_member", lambda e: log_inactivity(e))
```

**Use case:** Real-time monitoring

---

## 📊 Why Agent-First Matters

### 1. **Scalability**

Human-first tools don't scale:
- One human = one workflow
- Manual intervention required
- Hard to automate

Agent-first tools scale:
- Multiple agents = parallel workflows
- Fully automated
- Easy to replicate

---

### 2. **Reliability**

Human-first tools are fragile:
- Text output changes break parsers
- No error handling
- Manual recovery needed

Agent-first tools are robust:
- Stable JSON schemas
- Structured error handling
- Automatic retry/recovery

---

### 3. **Composability**

Human-first tools are isolated:
- Each tool is a snowflake
- No standard interface
- Hard to chain together

Agent-first tools compose:
- Standard JSON interface
- Easy to pipeline
- Dynamic workflow creation

---

### 4. **Maintainability**

Human-first tools drift:
- Output format changes
- No schema validation
- Breaking changes silent

Agent-first tools are stable:
- Documented schemas
- Versioned APIs
- Breaking changes explicit

---

## 🎓 Lessons from OpenClaw

This project follows patterns from [OpenClaw](https://github.com/openclaw/openclaw):

### 1. **Gateway Control Plane**

Single control plane for all tools:
```bash
# OpenClaw
openclaw agent --message "Check clan"

# RS-Agent
python3 tools/runescape-api.py --clan "Lords"
```

---

### 2. **Session Isolation**

Each agent gets isolated context:
```python
# Separate sessions for separate concerns
sessions_spawn(label="clan-monitor", task="...")
sessions_spawn(label="price-monitor", task="...")
```

---

### 3. **Skills Platform**

Tools as installable skills:
```bash
# OpenClaw skill
openclaw skills install rs-agent

# Usage
rs-clan-report --clan "Lords of Arcadia"
```

---

### 4. **JSON-First Philosophy**

Everything returns structured data:
```json
{
  "status": "success",
  "data": {...},
  "metadata": {...}
}
```

---

## 🚀 Getting Started

### For Humans

```bash
# Install
pip install -r requirements.txt

# Run tool
python3 tools/runescape-api.py --clan "Lords of Arcadia"
```

### For Agents

```bash
# Install
pip install -r requirements.txt

# Run tool with JSON output
python3 tools/runescape-api.py --clan "Lords of Arcadia" --json

# Parse with jq
python3 tools/runescape-api.py --clan "Lords" --json | jq '.total_members'
```

### For Multi-Agent Workflows

```python
from openclaw import sessions_spawn, sessions_send

# Spawn agents
sessions_spawn(label="rs-agent-1", task="Check clan caps")
sessions_spawn(label="rs-agent-2", task="Check inactive members")

# Send messages
sessions_send(session_key="rs-agent-1", message="Use --json flag")

# Collect results
results = collect_all_results()
```

---

## 📚 Further Reading

- [OpenClaw Vision](https://github.com/openclaw/openclaw/blob/main/VISION.md)
- [OpenClaw Architecture](https://docs.openclaw.ai/concepts/architecture)
- [Session Coordination](https://docs.openclaw.ai/concepts/session-tool)
- [Skills Platform](https://docs.openclaw.ai/tools/skills)

---

**Version:** 1.0.0  
**Manifesto Date:** March 17, 2026  
**Inspired by:** OpenClaw 🦞  
**Maintained by:** DuckBot / Franzferdinan51 🦆
