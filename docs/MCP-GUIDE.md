# 🤖 LM Studio MCP Integration Guide

Model Context Protocol (MCP) integration for RS-Agent-Skill-Lobster-Edition.

---

## 🎯 What is MCP?

Model Context Protocol (MCP) allows AI models (like LM Studio) to directly access external tools and data sources. With MCP, you can:

- Query RuneScape APIs directly from LM Studio
- Track your portfolio in real-time
- Get clan information during conversations
- Generate reports automatically
- Access both RS3 and OSRS data

---

## 📦 Prerequisites

1. **LM Studio** installed (https://lmstudio.ai/)
2. **Python 3.8+** installed
3. **RS-Agent toolkit** installed
4. **requests** library: `pip install requests`

---

## 🔧 Setup Instructions

### Step 1: Install RS-Agent Tools

```bash
# Clone repository
git clone https://github.com/Franzferdinan51/RS-Agent-Skill-Lobster-Edition.git
cd RS-Agent-Skill-Lobster-Edition

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure LM Studio

#### Option A: LM Studio UI (Recommended)

1. Open LM Studio
2. Go to **Settings** → **MCP Servers**
3. Click **Add Server**
4. Fill in:
   - **Name:** `runescape`
   - **Command:** `python3`
   - **Args:** `/full/path/to/mcp-server.py`
   - **Working Directory:** `/full/path/to/rs-agent-tools`
5. Click **Save**
6. Toggle server to **ON**

#### Option B: Configuration File

Create/edit LM Studio MCP config:

**macOS/Linux:**
```bash
~/.config/lmstudio/mcp-config.json
```

**Windows:**
```bash
%APPDATA%\LMStudio\mcp-config.json
```

Add this configuration:

```json
{
  "mcpServers": {
    "runescape": {
      "command": "python3",
      "args": ["/Users/duckets/.openclaw/workspace/rs-agent-tools/mcp-server.py"],
      "cwd": "/Users/duckets/.openclaw/workspace/rs-agent-tools",
      "env": {},
      "disabled": false
    }
  }
}
```

**Important:** Replace paths with your actual paths!

### Step 3: Verify Connection

1. In LM Studio, open a chat
2. Ask: "What RuneScape tools are available?"
3. LM Studio should list all 9 available tools

---

## 🛠️ Available MCP Tools

### 1. `runescape_api`
**Description:** Full RuneScape API client (GE, Hiscores, Clans, Runemetrics)

**Parameters:**
- `clan` (string): Clan name to lookup
- `player` (string): Player name to lookup
- `item` (string): Item name to search
- `item_id` (integer): Item ID for detail lookup
- `game` (string): "rs3" or "osrs" (default: "rs3")

**Example:**
```
Get clan info for Lords of Arcadia
```

---

### 2. `osrs_hiscores`
**Description:** Lookup Old School RuneScape player hiscores

**Parameters:**
- `player` (string, required): Player name
- `skills_only` (boolean): Show only skills
- `activities_only` (boolean): Show only activities

**Example:**
```
Look up Zezima's OSRS hiscores
```

---

### 3. `citadel_tracker`
**Description:** Track clan citadel capping activity

**Parameters:**
- `clan` (string, required): Clan name
- `since` (string): Date (YYYY-MM-DD), default: "2026-03-11"

**Example:**
```
Check citadel caps for Lords of Arcadia since March 11
```

---

### 4. `inactive_members`
**Description:** Find clan members inactive for X+ days

**Parameters:**
- `clan` (string, required): Clan name
- `days` (integer): Days of inactivity, default: 90

**Example:**
```
Find inactive members in Lords of Arcadia clan (90+ days)
```

---

### 5. `player_lookup`
**Description:** Comprehensive player profile lookup

**Parameters:**
- `player` (string, required): Player name
- `game` (string): "rs3" or "osrs" (default: "rs3")
- `full` (boolean): Include full profile with activity

**Example:**
```
Look up Zezima's full RS3 profile with activity
```

---

### 6. `price_alert`
**Description:** Monitor GE prices and alert on thresholds

**Parameters:**
- `item` (string, required): Item name
- `threshold` (integer, required): Price threshold
- `continuous` (boolean): Run continuously

**Example:**
```
Alert me when Twisted bow drops below 300m
```

---

### 7. `ge_arbitrage`
**Description:** Find GE arbitrage opportunities

**Parameters:**
- `scan_all` (boolean): Scan popular items, default: true
- `min_profit` (integer): Minimum profit, default: 10000
- `min_roi` (number): Minimum ROI %, default: 1.0

**Example:**
```
Find arbitrage opportunities with at least 2% ROI
```

---

### 8. `portfolio_tracker`
**Description:** Track RuneScape wealth and investments

**Parameters:**
- `action` (string, required): "view", "add", "remove", or "analyze"
- `item` (string): Item name (for add/remove)
- `quantity` (integer): Quantity (for add), default: 1
- `buy_price` (integer): Buy price per item (for add)

**Example:**
```
Add 1 Twisted bow to portfolio at 290m buy price
Show my current portfolio
```

---

### 9. `auto_report`
**Description:** Generate automated reports

**Parameters:**
- `type` (string, required): "daily", "weekly", "monthly", "clan", or "portfolio"
- `clan` (string): Clan name (for clan reports)
- `format` (string): "html", "json", or "markdown", default: "html"

**Example:**
```
Generate a clan report for Lords of Arcadia in HTML format
```

---

## 💡 Example Conversations

### Example 1: Clan Management

**You:** "Check my clan's citadel activity"

**LM Studio:** (uses `citadel_tracker` tool)
```json
{
  "capped": [
    {"player": "Zephryl", "cap_date": "2026-03-12"},
    {"player": "mike969122", "cap_date": "2026-03-12"}
  ]
}
```

**LM Studio:** "Your clan had 2 members cap at the citadel since March 11: Zephryl and mike969122, both on March 12th."

---

### Example 2: Portfolio Tracking

**You:** "I just bought a Scythe of Vitur for 500m"

**LM Studio:** (uses `portfolio_tracker` tool)
```json
{
  "status": "added",
  "item": {
    "name": "Scythe of vitur",
    "quantity": 1,
    "buy_price": 500000000
  }
}
```

**LM Studio:** "Added Scythe of vitur to your portfolio. Your total portfolio value is now..."

---

### Example 3: Price Monitoring

**You:** "What's the current price of Twisted bow?"

**LM Studio:** (uses `runescape_api` tool)
```json
{
  "item": {
    "name": "Twisted bow",
    "current": {"price": "295.5m", "trend": "neutral"}
  }
}
```

**LM Studio:** "Twisted bow is currently 295.5m gp with a neutral trend."

---

### Example 4: OSRS Hiscores

**You:** "What are Zezima's OSRS stats?"

**LM Studio:** (uses `osrs_hiscores` tool)
```json
{
  "player": "Zezima",
  "game": "OSRS",
  "skills": {
    "Overall": {"level": 1466, "rank": 1554618}
  }
}
```

**LM Studio:** "Zezima has a total level of 1466 in OSRS, ranked #1,554,618."

---

## 🔍 Troubleshooting

### MCP Server Not Connecting

**Check:**
1. Python path is correct
2. mcp-server.py path is absolute
3. Working directory is set
4. Python has execute permissions

**Test manually:**
```bash
python3 /path/to/mcp-server.py
# Should start without errors
```

### Tools Not Showing Up

**Check:**
1. MCP server is enabled in LM Studio
2. Server status shows as "connected"
3. Restart LM Studio
4. Check LM Studio logs for errors

### Tool Calls Failing

**Check:**
1. All dependencies installed: `pip install -r requirements.txt`
2. Tools are executable: `chmod +x tools/*.py`
3. Test tool manually: `python3 tools/runescape-api.py --clan "Lords"`

### Permission Errors

**Fix:**
```bash
# Make tools executable
chmod +x tools/*.py
chmod +x mcp-server.py

# If on macOS, may need to allow Python
# System Settings → Privacy & Security → Automation
```

---

## 📊 Advanced Configuration

### Environment Variables

Add to MCP config for API keys:

```json
{
  "mcpServers": {
    "runescape": {
      "command": "python3",
      "args": ["mcp-server.py"],
      "cwd": "/path/to/rs-agent-tools",
      "env": {
        "DISCORD_BOT_TOKEN": "your_token",
        "AGENTMAIL_API_KEY": "your_key"
      }
    }
  }
}
```

### Multiple MCP Servers

You can run multiple MCP servers:

```json
{
  "mcpServers": {
    "runescape": {
      "command": "python3",
      "args": ["mcp-server.py"],
      "cwd": "/path/to/rs-agent-tools"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/data"]
    }
  }
}
```

---

## 🎓 Best Practices

### 1. Use Clear Intentions
**Good:** "Check my clan's citadel caps"
**Better:** "Use citadel_tracker to check Lords of Arcadia caps since March 11"

### 2. Specify Parameters
**Good:** "Add item to portfolio"
**Better:** "Add 1 Twisted bow to portfolio at 290m buy price"

### 3. Request Specific Formats
**Good:** "Generate a report"
**Better:** "Generate a clan report in HTML format for email"

### 4. Combine Tools
**Example:**
```
1. Check clan info
2. Find inactive members
3. Generate a combined report
```

---

## 📚 Additional Resources

- **LM Studio Docs:** https://lmstudio.ai/docs
- **MCP Protocol:** https://modelcontextprotocol.io/
- **RS-Agent Tools:** See `README.md` in repository
- **Trading Guide:** `docs/TRADING-GUIDE.md`
- **Portfolio Guide:** `docs/PORTFOLIO-GUIDE.md`

---

## 🐛 Known Limitations

1. **Rate Limiting:** RuneScape APIs have rate limits (150ms between requests)
2. **OSRS GE:** OSRS doesn't have official GE API (limited functionality)
3. **Real-time Data:** Some data may be cached (check timestamps)
4. **Concurrent Calls:** MCP handles one tool call at a time

---

## 🆘 Support

**Issues:** Open issue on [GitHub](https://github.com/Franzferdinan51/RS-Agent-Skill-Lobster-Edition/issues)

**Discord:** Join [OpenClaw Discord](https://discord.gg/clawd)

**Documentation:** Check `docs/` directory

---

**Version:** 1.0.0  
**Last Updated:** March 17, 2026  
**Compatible:** LM Studio 0.2.20+
