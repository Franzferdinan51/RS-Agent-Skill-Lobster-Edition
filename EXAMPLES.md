# 📖 Examples - RS-Agent-Skill-Lobster-Edition

Real-world examples and copy-paste snippets for all tools.

---

## 🚀 Quick Start Examples

### Basic Clan Lookup

```bash
# Get clan info
python3 tools/runescape-api.py --clan "Lords of Arcadia"

# JSON output (for scripts)
python3 tools/runescape-api.py --clan "Lords of Arcadia" --json

# Save to file
python3 tools/runescape-api.py --clan "Lords of Arcadia" --json > clan.json
```

### Check Citadel Caps

```bash
# Check caps since date
python3 tools/citadel-cap-tracker.py --since "2026-03-11"

# Export to JSON
python3 tools/citadel-cap-tracker.py --since "2026-03-11" --output caps.json

# Different clan
python3 tools/citadel-cap-tracker.py --clan "Efficiency Experts" --since "2026-03-01"
```

### Find Inactive Members

```bash
# Find members inactive 90+ days
python3 tools/inactive-members.py --days 90

# Export results
python3 tools/inactive-members.py --days 90 --output inactive.json

# Show all members
python3 tools/inactive-members.py --days 90 --all
```

### Player Lookup

```bash
# Basic lookup
python3 tools/player-lookup.py --player "Zezima"

# Full profile
python3 tools/player-lookup.py --player "Zezima" --full

# OSRS only
python3 tools/player-lookup.py --player "Zezima" --osrs

# JSON output
python3 tools/player-lookup.py --player "Zezima" --json
```

---

## 🤖 Agent Integration Examples

### Python Script

```python
#!/usr/bin/env python3
"""Daily clan report generator."""

import subprocess
import json
from datetime import datetime

def get_clan_info(clan_name: str) -> dict:
    """Get clan information."""
    result = subprocess.run(
        ["python3", "tools/runescape-api.py", "--clan", clan_name, "--json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def get_citadel_caps(clan_name: str, since: str) -> dict:
    """Get citadel cap information."""
    result = subprocess.run(
        ["python3", "tools/citadel-cap-tracker.py", "--clan", clan_name, "--since", since, "--json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def generate_report(clan_name: str):
    """Generate daily clan report."""
    clan = get_clan_info(clan_name)
    caps = get_citadel_caps(clan_name, "2026-03-11")
    
    report = f"""
🛡️ {clan_name} Daily Report
{'=' * 50}

📊 Members: {clan['total_members']}
💫 Total XP: {clan['total_xp']:,}
✅ Citadel Caps: {len(caps['capped'])}

Top Members:
"""
    
    for i, member in enumerate(clan['top_members'][:5], 1):
        report += f"{i}. {member['name']} - {member['total_xp']:,} XP\n"
    
    print(report)
    return report

if __name__ == "__main__":
    generate_report("Lords of Arcadia")
```

### Multi-Agent Workflow

```python
#!/usr/bin/env python3
"""Multi-agent clan analysis."""

from openclaw import sessions_spawn, sessions_send

def analyze_clan(clan_name: str):
    """Spawn multiple agents to analyze clan."""
    
    # Spawn parallel agents
    sessions_spawn(
        label="citadel-agent",
        task=f"python3 tools/citadel-cap-tracker.py --clan '{clan_name}' --since '2026-03-11' --json"
    )
    
    sessions_spawn(
        label="inactive-agent",
        task=f"python3 tools/inactive-members.py --clan '{clan_name}' --days 90 --json"
    )
    
    sessions_spawn(
        label="stats-agent",
        task=f"python3 tools/runescape-api.py --clan '{clan_name}' --json"
    )
    
    # Collect results
    results = {}
    for agent in ["citadel-agent", "inactive-agent", "stats-agent"]:
        results[agent] = collect_result(agent)
    
    # Generate comprehensive report
    return generate_report(results)
```

### Price Monitoring Script

```python
#!/usr/bin/env python3
"""Continuous price monitoring with alerts."""

import time
import requests

ITEMS_TO_WATCH = [
    {"name": "Twisted bow", "threshold": 300000000},
    {"name": "Scythe of vitur", "threshold": 500000000},
    {"name": "Elder maul", "threshold": 100000000}
]

WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK"

def check_price(item_name: str, threshold: int):
    """Check item price and alert if below threshold."""
    result = subprocess.run(
        ["python3", "tools/runescape-api.py", "--item", item_name, "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    
    price_str = data.get("current", {}).get("price", "0")
    price = parse_price(price_str)  # Implement parse_price function
    
    if price <= threshold:
        send_alert(item_name, price, threshold)

def send_alert(item_name: str, price: int, threshold: int):
    """Send Discord webhook alert."""
    embed = {
        "title": "🚨 Price Alert!",
        "description": f"**{item_name}** is below threshold!",
        "fields": [
            {"name": "Current Price", "value": f"{price:,} gp"},
            {"name": "Threshold", "value": f"{threshold:,} gp"}
        ]
    }
    
    requests.post(WEBHOOK_URL, json={"embeds": [embed]})

# Main loop
while True:
    for item in ITEMS_TO_WATCH:
        check_price(item["name"], item["threshold"])
    time.sleep(3600)  # Check every hour
```

---

## 📧 Email Integration

### Send Clan Report via Email

```python
#!/usr/bin/env python3
"""Email clan report using AgentMail."""

import subprocess
import json

def send_clan_email(clan_name: str, recipient: str):
    """Send clan report via email."""
    
    # Get clan data
    result = subprocess.run(
        ["python3", "tools/runescape-api.py", "--clan", clan_name, "--json"],
        capture_output=True,
        text=True
    )
    clan = json.loads(result.stdout)
    
    # Generate HTML email
    html = f"""
    <html>
    <body>
        <h1>🛡️ {clan_name} Report</h1>
        <p><strong>Members:</strong> {clan['total_members']}</p>
        <p><strong>Total XP:</strong> {clan['total_xp']:,}</p>
        <p><strong>Average XP:</strong> {clan['average_xp']:,}</p>
        
        <h2>Top Members</h2>
        <ol>
    """
    
    for member in clan['top_members'][:10]:
        html += f"<li>{member['name']} - {member['total_xp']:,} XP</li>"
    
    html += """
        </ol>
    </body>
    </html>
    """
    
    # Send email using AgentMail
    subprocess.run([
        "python3", "skills/agentmail/scripts/send_email.py",
        "--inbox", "duckbot@agentmail.to",
        "--to", recipient,
        "--subject", f"{clan_name} Clan Report",
        "--html", html
    ])

# Usage
send_clan_email("Lords of Arcadia", "Optica5150@gmail.com")
```

---

## ⏰ Automation Examples

### Cron Jobs

```bash
# Daily clan report at 8 AM
0 8 * * * cd /path/to/rs-agent-tools && \
  python3 tools/runescape-api.py --clan "Lords of Arcadia" --json | \
  python3 scripts/send-email.py --to user@example.com

# Citadel check every 6 hours
0 */6 * * * cd /path/to/rs-agent-tools && \
  python3 tools/citadel-cap-tracker.py --clan "Lords of Arcadia" --since "2026-03-11" --json | \
  python3 scripts/check-caps.py

# Inactive member check weekly (Monday 9 AM)
0 9 * * 1 cd /path/to/rs-agent-tools && \
  python3 tools/inactive-members.py --clan "Lords of Arcadia" --days 30 --json | \
  python3 scripts/inactive-report.py

# Price monitoring every hour
0 * * * * cd /path/to/rs-agent-tools && \
  python3 tools/price-alert.py --watch-list config/watchlist.json --webhook https://discord.com/webhook/...
```

### Systemd Timer

```ini
# /etc/systemd/system/rs-clan-report.timer
[Unit]
Description=Daily RS Clan Report

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/rs-clan-report.service
[Unit]
Description=RS Clan Report Service

[Service]
Type=oneshot
User=duckets
WorkingDirectory=/path/to/rs-agent-tools
ExecStart=/usr/bin/python3 tools/runescape-api.py --clan "Lords of Arcadia" --json
```

---

## 🎮 Discord Bot Examples

### Setup Discord Bot

```bash
# Install dependencies
pip install discord.py python-dotenv

# Create .env file
echo "DISCORD_BOT_TOKEN=your_token_here" > .env

# Run bot
python3 discord-bot/bot.py

# Invite bot to server
# https://discord.com/api/oauth2/authorize?client_id=YOUR_ID&permissions=274878024768&scope=bot%20applications.commands
```

### Use Bot Commands

```
/rs-clan clan:Lords of Arcadia
/rs-player player:Zezima
/rs-item item:Twisted bow
/rs-citadel clan:Lords of Arcadia since:2026-03-11
/rs-inactive clan:Lords of Arcadia days:90
/rs-price-alert item:Twisted bow threshold:300000000
```

---

## 📊 Data Analysis Examples

### Analyze Clan Trends

```python
#!/usr/bin/env python3
"""Analyze clan activity trends over time."""

import json
import pandas as pd
import matplotlib.pyplot as plt

# Load historical data
with open("clan_history.json", "r") as f:
    history = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(history)

# Plot XP growth
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['total_xp'])
plt.title("Clan XP Growth Over Time")
plt.xlabel("Date")
plt.ylabel("Total XP")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("xp_growth.png")

# Plot member count
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['member_count'])
plt.title("Member Count Over Time")
plt.xlabel("Date")
plt.ylabel("Members")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("member_count.png")
```

---

## 🔧 Advanced Examples

### Batch Player Lookup

```python
#!/usr/bin/env python3
"""Lookup multiple players in parallel."""

import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

def lookup_player(player_name: str) -> dict:
    """Lookup single player."""
    result = subprocess.run(
        ["python3", "tools/player-lookup.py", "--player", player_name, "--json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

# List of players to lookup
players = ["Zezima", "Runescape", "Solo Mission", "Virtue", "Settled"]

# Parallel lookup
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(lookup_player, players))

# Process results
for result in results:
    if "error" not in result:
        print(f"{result['player']}: Level {result['skills']['Overall']['level']}")
    else:
        print(f"{result['player']}: {result['error']}")
```

### Custom API Client

```python
#!/usr/bin/env python3
"""Custom API client with caching."""

import requests
import json
from datetime import datetime, timedelta

class RuneScapeClient:
    def __init__(self, cache_ttl=3600):
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    def get_clan_info(self, clan_name: str) -> dict:
        """Get clan info with caching."""
        cache_key = f"clan:{clan_name}"
        
        # Check cache
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        # Fetch from API
        url = f"https://secure.runescape.com/m=clan-hiscores/members_lite.ws?clanName={clan_name.replace(' ', '+')}"
        response = requests.get(url)
        data = self.parse_clan_data(response.text)
        
        # Cache result
        self.cache[cache_key] = (datetime.now(), data)
        
        return data
    
    def parse_clan_data(self, csv_text: str) -> dict:
        """Parse clan CSV data."""
        lines = csv_text.strip().split("\n")
        members = []
        
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) >= 3:
                members.append({
                    "name": parts[0],
                    "rank": parts[1],
                    "xp": int(parts[2])
                })
        
        return {
            "total_members": len(members),
            "members": members
        }

# Usage
client = RuneScapeClient()
clan = client.get_clan_info("Lords of Arcadia")
print(f"Members: {clan['total_members']}")
```

---

## 📚 More Examples

- [OpenClaw Integration](AGENTS.md)
- [Agent-First Patterns](AGENT-FIRST.md)
- [API Reference](docs/API-REFERENCE.md)
- [Discord Bot](discord-bot/README.md)

---

**Version:** 1.0.0  
**Last Updated:** March 17, 2026  
**Maintained by:** DuckBot / Franzferdinan51
