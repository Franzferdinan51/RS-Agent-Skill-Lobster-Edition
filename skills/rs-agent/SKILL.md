# 🦆 RS-Agent Skill for OpenClaw

RuneScape API integration skill for OpenClaw agents.

---

## 📦 Installation

```bash
# Clone repository
cd ~/.openclaw/workspace
git clone https://github.com/Franzferdinan51/RS-Agent-Skill-Lobster-Edition.git rs-agent-tools

# Install dependencies
cd rs-agent-tools
pip install -r requirements.txt

# Enable skill (add to openclaw.json)
# See config example below
```

---

## 🛠️ Available Commands

### Clan Commands

```bash
# Get clan info
rs-clan-report --clan "Lords of Arcadia"

# List clan members
rs-clan-members --clan "Lords of Arcadia" --limit 20

# Check citadel caps
rs-citadel-check --clan "Lords of Arcadia" --since "2026-03-11"

# Find inactive members
rs-inactive-check --clan "Lords of Arcadia" --days 90
```

### Player Commands

```bash
# Lookup player
rs-player-lookup --player "Zezima"

# Full profile
rs-player-profile --player "Zezima" --full
```

### Item Commands

```bash
# Search item
rs-item-search --name "Twisted bow"

# Get price
rs-item-price --id 21787

# Check price history
rs-item-history --id 21787
```

---

## 🔧 OpenClaw Configuration

Add to `~/.openclaw/workspace/config/openclaw.json`:

```json
{
  "skills": {
    "rs-agent": {
      "enabled": true,
      "location": "~/.openclaw/workspace/rs-agent-tools/skills/rs-agent",
      "commands": {
        "rs-clan-report": {
          "description": "Get clan information and statistics",
          "script": "tools/runescape-api.py",
          "args": ["--clan", "{{clan_name}}", "--json"]
        },
        "rs-citadel-check": {
          "description": "Check clan citadel capping activity",
          "script": "tools/citadel-cap-tracker.py",
          "args": ["--clan", "{{clan_name}}", "--since", "{{since_date}}", "--json"]
        },
        "rs-inactive-check": {
          "description": "Find inactive clan members",
          "script": "tools/inactive-members.py",
          "args": ["--clan", "{{clan_name}}", "--days", "{{days}}", "--json"]
        },
        "rs-player-lookup": {
          "description": "Lookup player hiscores",
          "script": "tools/player-lookup.py",
          "args": ["--player", "{{player_name}}", "--json"]
        },
        "rs-item-search": {
          "description": "Search Grand Exchange items",
          "script": "tools/runescape-api.py",
          "args": ["--item", "{{item_name}}", "--json"]
        }
      }
    }
  }
}
```

---

## 🤖 Usage from OpenClaw Agent

### Example: Daily Clan Report

```python
# In your OpenClaw agent session
from openclaw import exec

# Get clan info
clan_data = exec("rs-clan-report --clan 'Lords of Arcadia' --json")

# Get citadel caps
caps = exec("rs-citadel-check --clan 'Lords of Arcadia' --since '2026-03-11' --json")

# Get inactive members
inactive = exec("rs-inactive-check --clan 'Lords of Arcadia' --days 90 --json")

# Generate report
report = f"""
🛡️ Lords of Arcadia Daily Report

📊 Members: {clan_data['total_members']}
💫 Total XP: {clan_data['total_xp']:,}
✅ Citadel Caps: {len(caps['capped'])}
⚠️ Inactive: {len(inactive['inactive_members'])}
"""

# Send to Telegram
message.send(channel="telegram", target="@Duckets", message=report)
```

---

### Example: Price Alert

```python
from openclaw import exec, message

# Check item price
item = exec("rs-item-search --name 'Twisted bow' --json")
price = int(item['current']['price'].replace('m', '000000'))

# Alert if below threshold
if price < 300000000:  # 300m
    message.send(
        channel="telegram",
        target="@Duckets",
        message=f"🚨 Price Alert! Twisted bow: {price:,} gp"
    )
```

---

### Example: Multi-Agent Clan Analysis

```python
from openclaw import sessions_spawn, sessions_send

# Spawn parallel agents
sessions_spawn(
    label="citadel-agent",
    task="rs-citadel-check --clan 'Lords of Arcadia' --since '2026-03-11' --json"
)

sessions_spawn(
    label="inactive-agent",
    task="rs-inactive-check --clan 'Lords of Arcadia' --days 90 --json"
)

sessions_spawn(
    label="stats-agent",
    task="rs-clan-report --clan 'Lords of Arcadia' --json"
)

# Wait for completion and collect results
results = collect_all_results()

# Generate comprehensive report
generate_report(results)
```

---

## 📊 Output Format

All commands return JSON for easy parsing:

### Clan Report

```json
{
  "clan_name": "Lords of Arcadia",
  "total_members": 219,
  "total_xp": 59789992303,
  "average_xp": 273013663,
  "rank_distribution": {
    "Recruit": 127,
    "Admin": 43
  }
}
```

### Citadel Check

```json
{
  "clan": "Lords of Arcadia",
  "since": "2026-03-11",
  "capped": [
    {
      "player": "Zephryl",
      "cap_date": "2026-03-12T11:55:00"
    }
  ]
}
```

### Inactive Check

```json
{
  "clan": "Lords of Arcadia",
  "inactive_members": [
    {
      "player": "Exlibrius",
      "days_inactive": 4565,
      "last_active": "2013-09-15"
    }
  ]
}
```

---

## 🔄 Automation Examples

### Daily Clan Report (Cron)

```bash
# Add to crontab
0 8 * * * cd ~/.openclaw/workspace/rs-agent-tools && \
  python3 tools/runescape-api.py --clan "Lords of Arcadia" --json | \
  python3 scripts/daily-report.py | \
  openclaw message send --to @Duckets
```

### Weekly Inactive Cleanup

```bash
# Add to crontab
0 9 * * 1 cd ~/.openclaw/workspace/rs-agent-tools && \
  python3 tools/inactive-members.py --clan "Lords of Arcadia" --days 30 --json | \
  python3 scripts/inactive-report.py | \
  openclaw message send --to @clan-leaders
```

### Continuous Price Monitoring

```python
# monitor.py
import time
from openclaw import exec, message

ITEMS = [
    ("Twisted bow", 300000000),
    ("Scythe of vitur", 500000000),
    ("Elder maul", 100000000)
]

while True:
    for item_name, threshold in ITEMS:
        result = exec(f"rs-item-search --name '{item_name}' --json")
        price = parse_price(result['current']['price'])
        
        if price < threshold:
            message.send(
                channel="telegram",
                target="@Duckets",
                message=f"🚨 {item_name}: {price:,} gp (threshold: {threshold:,})"
            )
    
    time.sleep(3600)  # Check every hour
```

---

## 🎯 Best Practices

### 1. Always Use JSON

```bash
# ✅ Good
rs-clan-report --clan "Lords" --json | jq '.total_members'

# ❌ Bad
rs-clan-report --clan "Lords" | grep "Members"
```

### 2. Handle Errors

```python
result = exec("rs-player-lookup --player 'Unknown' --json")
if "error" in result:
    log(f"Player not found: {result['error']}")
    return
```

### 3. Rate Limiting

```python
# Space out requests
for member in clan_members:
    result = exec(f"rs-player-lookup --player '{member}' --json")
    time.sleep(0.2)  # 200ms between requests
```

### 4. Use Sessions for Parallel Work

```python
# ✅ Good - parallel
sessions_spawn(label="agent1", task="check clan")
sessions_spawn(label="agent2", task="check players")

# ❌ Bad - sequential
check_clan()
check_players()
```

---

## 📚 Resources

- [Main Repository](https://github.com/Franzferdinan51/RS-Agent-Skill-Lobster-Edition)
- [API Reference](docs/API-REFERENCE.md)
- [Agent-First Guide](AGENT-FIRST.md)
- [OpenClaw Docs](https://docs.openclaw.ai)

---

**Version:** 1.0.0  
**Skill ID:** rs-agent  
**Author:** DuckBot / Franzferdinan51  
**License:** MIT
