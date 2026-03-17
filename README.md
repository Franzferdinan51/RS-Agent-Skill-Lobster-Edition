# 🦆 RS-Agent-Skill-Lobster-Edition

Comprehensive RuneScape API tools and scripts for AI agents and automation.

## 🚀 Features

- **Grand Exchange API** - Item prices, trends, categories, 180-day history
- **Hiscores API** - Player stats, rankings, skill tracking (RS3 + OSRS)
- **Clan API** - Member lists, stats, citadel tracking
- **Runemetrics API** - Activity logs, quest completion, XP tracking
- **Citadel Cap Tracker** - Monitor clan citadel capping activity
- **Inactive Member Tracker** - Find clan members inactive for X+ days
- **Agent-Friendly** - JSON output, CLI tools, Python library

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/Franzferdinan51/RS-Agent-Skill-Lobster-Edition.git
cd RS-Agent-Skill-Lobster-Edition

# Install dependencies
pip install -r requirements.txt

# Make tools executable
chmod +x tools/*.py
```

## 🛠️ Tools

### 1. RuneScape API Client (`tools/runescape-api.py`)

Full-featured API client for all RuneScape endpoints.

```bash
# Clan information
python3 tools/runescape-api.py --clan "Lords of Arcadia"

# Clan members list
python3 tools/runescape-api.py --clan-members "Lords of Arcadia" --limit 20

# Player hiscores
python3 tools/runescape-api.py --player "Zezima"

# Item search
python3 tools/runescape-api.py --item "Twisted bow"

# Top clans
python3 tools/runescape-api.py --top-clans

# JSON output
python3 tools/runescape-api.py --clan "Lords of Arcadia" --json
```

### 2. Citadel Cap Tracker (`tools/citadel-cap-tracker.py`)

Track clan members who have capped at the clan citadel since a specified date.

```bash
# Check caps since March 11, 2026
python3 tools/citadel-cap-tracker.py --since "2026-03-11"

# Export to JSON
python3 tools/citadel-cap-tracker.py --since "2026-03-11" --output caps.json

# Different clan
python3 tools/citadel-cap-tracker.py --clan "Efficiency Experts" --since "2026-03-01"
```

### 3. Inactive Member Tracker (`tools/inactive-members.py`)

Find clan members who haven't been active for X+ days.

```bash
# Find members inactive 90+ days
python3 tools/inactive-members.py --days 90

# Export results
python3 tools/inactive-members.py --days 90 --output inactive.json

# Show all members with activity
python3 tools/inactive-members.py --days 90 --all
```

### 4. Player Lookup (`tools/player-lookup.py`)

Comprehensive player profile lookup across RS3 and OSRS.

```bash
# Basic lookup
python3 tools/player-lookup.py --player "Zezima"

# Full profile with activity
python3 tools/player-lookup.py --player "Zezima" --full

# OSRS only
python3 tools/player-lookup.py --player "Zezima" --osrs

# JSON output
python3 tools/player-lookup.py --player "Zezima" --json
```

### 5. Clan Analyzer (`tools/clan-analyzer.py`)

Comprehensive clan analysis with statistics and member breakdown.

```bash
# Full clan analysis
python3 tools/clan-analyzer.py --clan "Lords of Arcadia"

# Export analysis
python3 tools/clan-analyzer.py --clan "Lords of Arcadia" --output analysis.json

# Compare multiple clans
python3 tools/clan-analyzer.py --clan "Lords of Arcadia" --clan "Efficiency Experts"
```

## 📖 API Documentation

See `docs/API-REFERENCE.md` for complete API endpoint documentation.

### Quick Reference

| API | Base URL | Endpoints |
|-----|----------|-----------|
| Grand Exchange | `https://secure.runescape.com/m=itemdb_rs/api` | `/info.json`, `/catalogue/detail.json`, `/graph/{id}.json` |
| Hiscores | `https://secure.runescape.com/m=hiscore` | `/index_lite.ws`, `/ranking.json` |
| Clan | `https://secure.runescape.com/m=clan-hiscores` | `/clanRanking.json`, `/members_lite.ws` |
| Runemetrics | `https://apps.runescape.com/runemetrics` | `/profile/profile`, `/quests`, `/xp-monthly` |

## 🤖 Agent Integration

### Python Library

```python
from tools.runescape_api import RuneScapeAPI

api = RuneScapeAPI()

# Get clan info
clan = api.get_clan_info("Lords of Arcadia")
print(f"Members: {clan['total_members']}")

# Get player stats
player = api.get_player_stats("Zezima")
print(f"Level: {player['skills']['Overall']['level']}")

# Check citadel caps
caps = api.check_citadel_caps("Lords of Arcadia", since="2026-03-11")
print(f"Capped: {len(caps)} members")
```

### CLI for Agents

All tools support JSON output for easy agent integration:

```bash
# Get clan data as JSON
clan_data=$(python3 tools/runescape-api.py --clan "Lords of Arcadia" --json)

# Parse with jq
echo $clan_data | jq '.total_members'
```

## 📊 Example Output

### Clan Info
```
🛡️  Clan: Lords of Arcadia
==================================================
👥 Members: 219
💫 Total XP: 59.79B
📊 Average XP: 273.01M
⚔️  Total Kills: 33

📋 Rank Distribution:
   Recruit: 127
   Admin: 43
   Sergeant: 10
   ...
```

### Citadel Caps
```
✅ CAPPED CITADEL (3 members since Mar 11):
------------------------------------------------------------
#    Player       Cap Date               Total XP
------------------------------------------------------------
1    mike969122   Mar 12, 2026 01:07 PM  1,247,443,618
2    Zephryl      Mar 12, 2026 11:55 AM  3,874,347,529
3    Tyneelegs    Mar 12, 2026 11:51 AM  412,526,882
```

## 🔧 Configuration

Create `config/config.json` for default settings:

```json
{
  "default_clan": "Lords of Arcadia",
  "default_days_inactive": 90,
  "rate_limit_ms": 150,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RS-Agent/1.0",
  "output_format": "json",
  "cache_enabled": true,
  "cache_ttl_seconds": 3600
}
```

## ⚠️ Rate Limiting

- RuneScape APIs have request throttling
- Default rate limit: 150ms between requests
- Adjust in `config/config.json` or with `--rate-limit` flag
- Be respectful - these are free public APIs

## 📝 License

MIT License - See LICENSE file

## 🦆 Credits

Created for DuckBot's Lords of Arcadia clan tracking and analysis.

---

**Version:** 1.0.0  
**Last Updated:** March 17, 2026  
**Status:** ✅ Operational
