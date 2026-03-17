# 🦆 RS-Agent-Skill-Lobster-Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord Bot](https://img.shields.io/badge/Discord-Bot-7289da.svg)](https://discord.com/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Agent--First-FF4500.svg)](https://github.com/openclaw/openclaw)

Comprehensive RuneScape API tools and scripts for AI agents and automation.

## 🚀 Features

### CLI Tools
- **Grand Exchange API** - Item prices, trends, categories, 180-day history
- **Hiscores API** - Player stats, rankings, skill tracking (RS3 + OSRS)
- **Clan API** - Member lists, stats, citadel tracking
- **Runemetrics API** - Activity logs, quest completion, XP tracking
- **Citadel Cap Tracker** - Monitor clan citadel capping activity
- **Inactive Member Tracker** - Find clan members inactive for X+ days
- **Price Alert Monitor** - GE price monitoring with webhook alerts

### 🤖 Discord Bot
- **Slash Commands** - 7 RuneScape commands for your server
- **Beautiful Embeds** - Formatted responses with colors, thumbnails, fields
- **Auto-Posting** - Daily reports, price alerts, activity summaries
- **Interactive** - Buttons, dropdowns, pagination, modals
- **Dashboard** - Live clan statistics and activity graphs
- **Admin Commands** - Server configuration and management

### Agent Integration
- **Agent-Friendly** - JSON output, CLI tools, Python library
- **OpenClaw Skills** - Native OpenClaw integration
- **Multi-Agent** - Parallel processing and session coordination
- **Webhooks** - Discord, Slack, custom webhook support

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

## 🛠️ CLI Tools

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

## 🤖 Discord Bot Setup

Full-featured Discord bot with slash commands, embeds, and auto-posting.

### Quick Setup

```bash
# 1. Install Discord dependencies
pip install discord.py python-dotenv

# 2. Create Discord Application
# Go to: https://discord.com/developers/applications
# Click "New Application" → Name it → Go to "Bot" section
# Click "Add Bot" → Copy bot token

# 3. Create .env file
cat > .env << EOF
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id_here
EOF

# 4. Run the bot
python3 discord-bot/bot.py

# 5. Invite to your server
# Replace YOUR_CLIENT_ID with your actual client ID
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274878024768&scope=bot%20applications.commands
```

### Required Permissions

- **Read Messages/View Channels**
- **Send Messages**
- **Embed Links**
- **Attach Files**
- **Add Reactions**
- **Use Application Commands**
- **Manage Webhooks** (for alerts)

### Slash Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/rs-clan` | Get clan information | `/rs-clan clan:Lords of Arcadia` |
| `/rs-player` | Lookup player stats | `/rs-player player:Zezima` |
| `/rs-item` | Check GE price | `/rs-item item:Twisted bow` |
| `/rs-citadel` | Check citadel caps | `/rs-citadel clan:Lords of Arcadia since:2026-03-11` |
| `/rs-inactive` | Find inactive members | `/rs-inactive clan:Lords of Arcadia days:90` |
| `/rs-price-alert` | Set price alert | `/rs-price-alert item:Twisted bow threshold:300000000` |
| `/rs-track` | Track player progress | `/rs-track player:Zezima skill:Attack` |

### Configuration

Create `discord-bot/config/servers.json`:

```json
{
  "servers": {
    "YOUR_SERVER_ID": {
      "clan_name": "Lords of Arcadia",
      "alert_channel": "ALERT_CHANNEL_ID",
      "report_channel": "REPORT_CHANNEL_ID",
      "alert_role": "ALERT_ROLE_ID",
      "auto_post": {
        "daily_report": true,
        "citadel_caps": true,
        "price_alerts": true
      }
    }
  }
}
```

### Auto-Posting Features

The bot can automatically post:

- **Daily Clan Reports** - Every day at 8 AM
- **Citadel Cap Alerts** - When members cap (hourly check)
- **Price Alerts** - When prices cross thresholds
- **Activity Summaries** - Weekly member activity

### Interactive Features

- **Buttons** - Refresh data, navigate pages, export
- **Dropdowns** - Select clans, items, time ranges
- **Pagination** - Navigate through large results
- **Modals** - Configure alerts, track players
- **Dashboard** - `/rs-dashboard` for live clan stats

### Troubleshooting

**Bot not responding?**
1. Check bot token in `.env`
2. Ensure bot is online (green dot)
3. Check Message Content Intent is enabled
4. Verify bot permissions in server

**Commands not showing?**
1. Wait up to 1 hour for registration
2. Re-invite bot to server
3. Run `python3 discord-bot/setup.py` to re-register

**See full documentation:** [`discord-bot/README.md`](discord-bot/README.md)

---

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

## 📚 Documentation

| File | Description |
|------|-------------|
| [`AGENTS.md`](AGENTS.md) | Agent-first architecture and OpenClaw integration |
| [`AGENT-FIRST.md`](AGENT-FIRST.md) | Why agent-first design matters |
| [`EXAMPLES.md`](EXAMPLES.md) | Copy-paste ready examples and workflows |
| [`docs/API-REFERENCE.md`](docs/API-REFERENCE.md) | Complete API endpoint reference |
| [`discord-bot/README.md`](discord-bot/README.md) | Discord bot setup and usage |
| [`skills/rs-agent/SKILL.md`](skills/rs-agent/SKILL.md) | OpenClaw skill configuration |

## ⚠️ Rate Limiting

- RuneScape APIs have request throttling
- Default rate limit: 150ms between requests
- Adjust in `config/config.json` or with `--rate-limit` flag
- Be respectful - these are free public APIs

## 🤝 Contributing

Contributions welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 🦆 Credits

Created for DuckBot's Lords of Arcadia clan tracking and analysis.

Inspired by [OpenClaw](https://github.com/openclaw/openclaw) agent-first philosophy.

## 🔗 Links

- **Repository:** https://github.com/Franzferdinan51/RS-Agent-Skill-Lobster-Edition
- **OpenClaw:** https://github.com/openclaw/openclaw
- **Discord:** https://discord.gg/clawd
- **RuneScape Wiki API:** https://runescape.wiki/w/Application_programming_interface

---

**Version:** 1.0.0  
**Last Updated:** March 17, 2026  
**Status:** ✅ Operational  
**Total Tools:** 5 CLI + Discord Bot  
**Total Docs:** 7 files
