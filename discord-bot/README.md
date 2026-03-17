# 🤖 Discord Bot for RS-Agent

RuneScape Discord bot with slash commands, embeds, and auto-posting.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install discord.py python-dotenv
```

### 2. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Go to "Bot" section
4. Click "Add Bot"
5. Copy bot token
6. Enable "Message Content Intent"

### 3. Configure Bot

Create `.env` file:

```bash
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id_here
```

### 4. Run Bot

```bash
python3 discord-bot/bot.py
```

### 5. Invite Bot to Server

```bash
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274878024768&scope=bot%20applications.commands
```

---

## 🎮 Slash Commands

### Clan Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/rs-clan` | Get clan information | `/rs-clan clan:Lords of Arcadia` |
| `/rs-citadel` | Check citadel capping | `/rs-citadel clan:Lords of Arcadia since:2026-03-11` |
| `/rs-inactive` | Find inactive members | `/rs-inactive clan:Lords of Arcadia days:90` |

### Player Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/rs-player` | Lookup player stats | `/rs-player player:Zezima` |
| `/rs-track` | Track player progress | `/rs-track player:Zezima skill:Attack` |

### Item Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/rs-item` | Check GE price | `/rs-item item:Twisted bow` |
| `/rs-price-alert` | Set price alert | `/rs-price-alert item:Twisted bow threshold:300000000` |

---

## 🎨 Embed Examples

### Clan Info Embed

```
🛡️ Lords of Arcadia
━━━━━━━━━━━━━━━━━━━━
👥 Members: 219
💫 Total XP: 59.79B
📊 Average XP: 273.01M
⚔️  Total Kills: 33

Rank Distribution:
• Recruit: 127
• Admin: 43
• Sergeant: 10
...
```

### Price Alert Embed

```
🚨 Price Alert!
━━━━━━━━━━━━━━━━━━━━
Twisted bow has crossed your threshold!

Current Price: 295,000,000 gp
Threshold:     300,000,000 gp
Difference:    -5,000,000 gp

[View on GE](https://secure.runescape.com/m=itemdb_rs)
```

---

## ⚙️ Configuration

### Server Config (`config/servers.json`)

```json
{
  "servers": {
    "123456789012345678": {
      "clan_name": "Lords of Arcadia",
      "alert_channel": "987654321098765432",
      "report_channel": "876543210987654321",
      "alert_role": "765432109876543210",
      "auto_post": {
        "daily_report": true,
        "citadel_caps": true,
        "price_alerts": true
      }
    }
  }
}
```

### Watch List (`config/watchlist.json`)

```json
{
  "items": [
    {"name": "Twisted bow", "threshold": 300000000},
    {"name": "Scythe of vitur", "threshold": 500000000},
    {"name": "Elder maul", "threshold": 100000000}
  ]
}
```

---

## 🔔 Auto-Posting

### Daily Clan Report

Posts every day at 8 AM:

```python
# Auto-posts to configured channel
- Clan statistics
- Member count changes
- XP gains
- Citadel cap count
```

### Citadel Cap Alerts

Posts when members cap:

```python
# Monitors every hour
- New citadel caps
- Member name
- Cap timestamp
```

### Price Alerts

Posts when prices cross thresholds:

```python
# Monitors continuously
- Item name
- Current price
- Threshold
- Price difference
```

---

## 🎯 Interactive Components

### Buttons

- **Refresh** - Update embed with latest data
- **Next/Previous** - Paginate through results
- **Export** - Download data as CSV
- **Subscribe** - Get notified of updates

### Dropdowns

- **Clan Selection** - Choose from saved clans
- **Item Selection** - Choose from watch list
- **Time Range** - Select time period for reports

### Modals

- **Set Alert** - Configure price alert
- **Track Player** - Add player to tracking
- **Custom Report** - Configure report parameters

---

## 📊 Clan Dashboard

Live dashboard showing:

- **Member Count** - Real-time count
- **XP Gains** - Weekly/monthly totals
- **Activity Graph** - Member activity over time
- **Citadel Tracker** - Caps this week
- **Top Members** - Leaderboard by XP

Access with: `/rs-dashboard`

---

## 🛡️ Admin Commands

| Command | Permission | Description |
|---------|-----------|-------------|
| `/admin-config` | Admin | Configure bot settings |
| `/admin-alerts` | Admin | Manage alert channels |
| `/admin-export` | Admin | Export all data |
| `/admin-stats` | Admin | View bot statistics |
| `/admin-broadcast` | Admin | Send message to all servers |

---

## 🔧 Troubleshooting

### Bot Not Responding

1. Check bot token in `.env`
2. Ensure bot is online (green dot in Discord)
3. Check bot permissions in server
4. Verify Message Content Intent is enabled

### Commands Not Showing

1. Wait up to 1 hour for command registration
2. Kick and re-invite bot
3. Run `python3 discord-bot/setup.py` to re-register

### Alerts Not Posting

1. Check alert channel permissions
2. Verify webhook URL is correct
3. Check bot has "Send Messages" permission
4. Ensure channel ID is correct in config

---

## 📚 Resources

- [Discord.py Docs](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs)
- [RuneScape API](docs/API-REFERENCE.md)
- [RS-Agent Main Repo](https://github.com/Franzferdinan51/RS-Agent-Skill-Lobster-Edition)

---

**Version:** 1.0.0  
**Bot Version:** 1.0.0  
**Author:** DuckBot / Franzferdinan51  
**License:** MIT
