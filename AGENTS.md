# 🦞 AGENTS.md - Agent-First Architecture

This repository follows the **Agent-First** design philosophy from [OpenClaw](https://github.com/openclaw/openclaw).

---

## 🎯 Agent-First Principles

### 1. **JSON-First Output**
All tools support `--json` flag for structured output that agents can parse:

```bash
python3 tools/runescape-api.py --clan "Lords of Arcadia" --json
```

### 2. **Rate Limiting Built-In**
Every tool respects API rate limits with configurable delays:

```bash
python3 tools/citadel-cap-tracker.py --rate-limit 200  # 200ms between requests
```

### 3. **Error Handling for Agents**
All errors return structured JSON that agents can handle:

```json
{
  "error": "Player not found",
  "player": "UnknownPlayer"
}
```

### 4. **Session Coordination**
Tools can be chained together for multi-agent workflows:

```bash
# Agent 1: Get clan members
python3 tools/runescape-api.py --clan "Lords of Arcadia" --json > clan.json

# Agent 2: Process members
python3 tools/inactive-members.py --clan "Lords of Arcadia" --json > inactive.json

# Agent 3: Generate report
python3 scripts/generate-report.py --input inactive.json --output report.md
```

---

## 🤖 Multi-Agent Workflows

### Example: Clan Activity Monitor

```python
# orchestrator.py
from sessions_send import send_to_agent
import json

# Spawn parallel agents
agents = [
    ("citadel-agent", "Check citadel caps since 2026-03-11"),
    ("inactive-agent", "Find members inactive 90+ days"),
    ("stats-agent", "Calculate clan statistics")
]

results = {}
for agent_id, task in agents:
    send_to_agent(agent_id, task)

# Collect results
for agent_id, _, _ in agents:
    results[agent_id] = collect_result(agent_id)

# Aggregate
generate_report(results)
```

### Example: Price Monitoring Pipeline

```bash
#!/bin/bash
# price-monitor.sh

# Agent 1: Scan GE for item
ITEM_ID=$(python3 tools/runescape-api.py --item "Twisted bow" --json | jq '.id')

# Agent 2: Get price history
python3 tools/runescape-api.py --item-id $ITEM_ID --graph > price.json

# Agent 3: Check thresholds
python3 tools/price-alert.py --input price.json --threshold 300000000

# Agent 4: Send alert if needed
if [ $? -eq 0 ]; then
    openclaw message send --to @Duckets --message "Price alert!"
fi
```

---

## 📡 OpenClaw Integration

### Skill Configuration

Add to `~/.openclaw/workspace/config/openclaw.json`:

```json
{
  "skills": {
    "rs-agent": {
      "enabled": true,
      "path": "~/.openclaw/workspace/rs-agent-tools/skills/rs-agent",
      "commands": [
        "rs-clan-report",
        "rs-price-check",
        "rs-player-lookup"
      ]
    }
  }
}
```

### Using with OpenClaw Message Tool

```python
from openclaw import message

# Send clan report to Telegram
report = generate_clan_report("Lords of Arcadia")
message.send(
    channel="telegram",
    target="@Duckets",
    message=report,
    parse_mode="markdown"
)
```

### Session Coordination

```python
from openclaw import sessions

# Send to specific session
sessions.send(
    session_key="clan-monitor-session",
    message="Check Lords of Arcadia activity"
)

# Get session history
history = sessions.history(
    session_key="clan-monitor-session",
    limit=10
)
```

---

## 🛠️ Tool Reference for Agents

### runescape-api.py

```bash
# Get clan info
python3 tools/runescape-api.py --clan "Lords of Arcadia" --json

# Get player stats
python3 tools/runescape-api.py --player "Zezima" --json

# Get item details
python3 tools/runescape-api.py --item-id 21787 --json

# Get top clans
python3 tools/runescape-api.py --top-clans --limit 10 --json
```

### citadel-cap-tracker.py

```bash
# Check caps since date
python3 tools/citadel-cap-tracker.py --since "2026-03-11" --json

# Export to file
python3 tools/citadel-cap-tracker.py --since "2026-03-11" --output caps.json
```

### inactive-members.py

```bash
# Find inactive members
python3 tools/inactive-members.py --days 90 --json

# Include all members
python3 tools/inactive-members.py --days 90 --all --json
```

### player-lookup.py

```bash
# Basic lookup
python3 tools/player-lookup.py --player "Zezima" --json

# Full profile
python3 tools/player-lookup.py --player "Zezima" --full --json

# OSRS only
python3 tools/player-lookup.py --player "Zezima" --osrs --json
```

---

## 📊 Output Schemas

### Clan Info Response

```json
{
  "clan_name": "Lords of Arcadia",
  "total_members": 219,
  "total_xp": 59789992303,
  "average_xp": 273013663,
  "total_kills": 33,
  "rank_distribution": {
    "Recruit": 127,
    "Admin": 43,
    "Deputy Owner": 6
  },
  "top_members": [
    {
      "name": "mike96912",
      "rank": "Deputy Owner",
      "total_xp": 3497356447
    }
  ]
}
```

### Citadel Cap Response

```json
{
  "clan": "Lords of Arcadia",
  "since": "2026-03-11",
  "checked_at": "2026-03-17T18:42:00Z",
  "total_members": 219,
  "capped": [
    {
      "player": "Zephryl",
      "cap_date": "2026-03-12T11:55:00",
      "visit_date": "2026-03-12T11:34:00",
      "total_xp": 3874347529
    }
  ],
  "visited_only": []
}
```

### Player Lookup Response

```json
{
  "hiscores": {
    "player": "Zezima",
    "game": "RS3",
    "skills": {
      "Overall": {
        "rank": 6264,
        "level": 3200,
        "xp": 5710000000
      }
    }
  },
  "runemetrics": {
    "combatlevel": 152,
    "questscomplete": 356,
    "loggedIn": "false",
    "activities": [...]
  }
}
```

---

## 🔄 Retry Patterns

### Exponential Backoff

```python
import time
import requests

def api_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                wait_time = (2 ** attempt) * 1.5  # Exponential backoff
                time.sleep(wait_time)
        except requests.exceptions.Timeout:
            time.sleep(2 ** attempt)
    return None
```

### Rate Limit Handling

```python
def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = response.headers.get('Retry-After', 60)
        time.sleep(int(retry_after))
        return True
    return False
```

---

## 📝 Best Practices

### 1. Always Use JSON for Agents

```bash
# ✅ Good
python3 tools/runescape-api.py --clan "Lords" --json | jq '.total_members'

# ❌ Bad (requires parsing text)
python3 tools/runescape-api.py --clan "Lords" | grep "Members"
```

### 2. Handle Errors Gracefully

```python
result = api.get_clan_info("UnknownClan")
if "error" in result:
    log_error(result["error"])
    return None
```

### 3. Respect Rate Limits

```python
# ✅ Good
api = RuneScapeAPI(rate_limit_ms=200)

# ❌ Bad (will get rate limited)
api = RuneScapeAPI(rate_limit_ms=0)
```

### 4. Use Sessions for Coordination

```python
# ✅ Good - parallel processing
sessions_spawn(label="agent1", task="check clan")
sessions_spawn(label="agent2", task="check players")

# ❌ Bad - sequential
check_clan()
check_players()
```

---

## 🎓 Learning Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Session Coordination](https://docs.openclaw.ai/concepts/session-tool)
- [Skills Platform](https://docs.openclaw.ai/tools/skills)

---

**Version:** 1.0.0  
**Last Updated:** March 17, 2026  
**Maintained by:** DuckBot / Franzferdinan51
