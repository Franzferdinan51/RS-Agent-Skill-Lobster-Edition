# 🤖 LM Studio MCP Servers Configuration

Complete MCP server configuration for LM Studio with **14 free servers**!

---

## 📦 Configured Servers (14 Total)

### ✅ Enabled by Default (No API Key Required)

| Server | Purpose | Category | Status |
|--------|---------|----------|--------|
| **runescape** | RuneScape API (13 tools) | Gaming | ✅ Enabled |
| **sequential-thinking** | Problem-solving framework | Productivity | ✅ Enabled |
| **filesystem** | File operations | Development | ✅ Enabled |
| **git** | Git repository tools | Development | ✅ Enabled |
| **memory** | Knowledge graph memory | Productivity | ✅ Enabled |
| **fetch** | Web content fetching | Search | ✅ Enabled |
| **time** | Time/date operations | Utilities | ✅ Enabled |
| **sqlite** | Database queries | Development | ✅ Enabled |
| **jina-search** | AI search foundation | Search | ✅ Enabled |
| **puppeteer** | Browser automation | Development | ✅ Enabled |

### ⏸️ Disabled (Requires Free API Key)

| Server | Purpose | Free Tier | Status |
|--------|---------|-----------|--------|
| **brave-search** | Web search | 2,000 queries/month | ⏸️ Ready |
| **github** | GitHub API | 5,000 requests/hour | ⏸️ Ready |
| **weather** | Weather data | 60 calls/min | ⏸️ Ready |
| **everything** | Reference/test server | Unlimited | ⏸️ Ready |

---

## 🚀 Quick Setup

### 1. Enable All Free Servers (Recommended)

The configuration above has all **free servers enabled** by default. Just restart LM Studio!

### 2. Enable Paid Servers (Optional)

#### Brave Search (2,000 free queries/month)

1. **Get API Key:**
   - Visit: https://brave.com/search/api/
   - Sign up for free account
   - Generate API key

2. **Update Config:**
   ```json
   "brave-search": {
     "env": {
       "BRAVE_API_KEY": "YOUR_ACTUAL_KEY_HERE"
     },
     "disabled": false
   }
   ```

#### GitHub (5,000 requests/hour free)

1. **Get API Key:**
   - Visit: https://github.com/settings/tokens
   - Generate personal access token
   - Select scopes: `repo`, `read:user`

2. **Update Config:**
   ```json
   "github": {
     "env": {
       "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_ACTUAL_TOKEN_HERE"
     },
     "disabled": false
   }
   ```

#### Weather (60 calls/min free)

1. **Get API Key:**
   - Visit: https://openweathermap.org/api
   - Sign up for free account
   - Generate API key

2. **Update Config:**
   ```json
   "weather": {
     "env": {
       "WEATHER_API_KEY": "YOUR_ACTUAL_KEY_HERE"
     },
     "disabled": false
   }
   ```

---

## 🛠️ Server Details

### 🎮 runescape (Custom)
**Purpose:** RuneScape game data and tools  
**Tools:** 13 tools (clan tracking, GE prices, hiscores, portfolio, etc.)  
**Games:** RS3 + OSRS  
**Setup:** Already configured - points to your RS-Agent installation  

**Example Usage:**
```
Get clan info for Lords of Arcadia
Check Twisted bow price
Show my portfolio
Find arbitrage opportunities
```

---

### 🧠 sequential-thinking (NEW!)
**Purpose:** Structured problem-solving framework  
**Tools:** Process thoughts, generate summaries, clear history  
**Cost:** FREE - No API key needed  
**Setup:** No setup required  

**Example Usage:**
```
Help me think through this trading strategy step by step
Break down this complex problem
Generate a summary of our discussion
```

**Why It's Useful:**
- Break complex problems into manageable steps
- Reflective thinking process
- Perfect for trading strategy development
- Reduces impulsive decisions
- Creates documented thought process

---

### 🗄️ sqlite (NEW!)
**Purpose:** SQLite database operations  
**Tools:** Query databases, inspect schemas, explain queries  
**Cost:** FREE - No API key needed  
**Setup:** No setup required  

**Example Usage:**
```
Query my trading database
Show me the schema
Explain this query
```

**Why It's Useful:**
- Store trading history locally
- Query portfolio performance
- Analyze trading patterns
- No server required (file-based)

---

### 🌐 puppeteer (NEW!)
**Purpose:** Browser automation  
**Tools:** Navigate pages, take screenshots, extract content  
**Cost:** FREE - No API key needed  
**Setup:** No setup required  

**Example Usage:**
```
Take a screenshot of this webpage
Navigate to runescape.wiki and extract prices
Fill out this form
```

**Why It's Useful:**
- Automate web research
- Capture price data from websites
- Test web interfaces
- Bypass API limitations

---

### 🧪 everything (Optional)
**Purpose:** Reference/test server  
**Tools:** Prompts, resources, tools (demo)  
**Cost:** FREE - No API key needed  
**Setup:** No setup required  

**Example Usage:**
```
Test MCP functionality
Explore available tools
```

**Why It's Useful:**
- Learn MCP capabilities
- Test your MCP setup
- Reference implementation

---

### 📁 filesystem
**Purpose:** Secure file operations  
**Tools:** Read, write, search, list files  
**Access:** Limited to `/Users/duckets/.openclaw/workspace`  
**Setup:** No setup required  

**Example Usage:**
```
List files in my workspace
Read the README.md file
Search for Python files
```

---

### 🔧 git
**Purpose:** Git repository operations  
**Tools:** Read, search, diff, log  
**Setup:** No setup required  

**Example Usage:**
```
Show git status
List recent commits
Show diff for README.md
```

---

### 🧠 memory
**Purpose:** Persistent knowledge graph  
**Tools:** Store, retrieve, query memories  
**Setup:** No setup required  

**Example Usage:**
```
Remember that Duckets plays RS3
What do you know about my portfolio?
Store this trading strategy
```

---

### 🌐 fetch
**Purpose:** Web content fetching  
**Tools:** Fetch URLs, convert to markdown  
**Setup:** No setup required  

**Example Usage:**
```
Fetch this URL and summarize it
Get the content of https://example.com
```

---

### ⏰ time
**Purpose:** Time and date operations  
**Tools:** Current time, timezone conversion, date math  
**Setup:** No setup required  

**Example Usage:**
```
What time is it in Tokyo?
How many days until March 25?
Convert 3pm EST to PST
```

---

### 🔍 jina-search
**Purpose:** AI search foundation  
**Tools:** Web search, neural search  
**Free Tier:** Limited queries/day  
**Setup:** No setup required for basic tier  

**Example Usage:**
```
Search for latest AI news
Find information about MCP servers
```

---

### 🦅 brave-search (Optional)
**Purpose:** Full web search  
**Tools:** Web search, local search, news, images  
**Free Tier:** 2,000 queries/month  
**Setup:** Requires BRAVE_API_KEY  

**Example Usage:**
```
What are the latest Next.js updates?
Search for RuneScape trading guides
Find news about AI developments
```

---

### 🐙 github (Optional)
**Purpose:** GitHub integration  
**Tools:** Repo search, issues, users, content  
**Free Tier:** 5,000 requests/hour  
**Setup:** Requires GITHUB_PERSONAL_ACCESS_TOKEN  

**Example Usage:**
```
Search for MCP servers on GitHub
Show issues in openclaw/openclaw
Get user info for Franzferdinan51
```

---

### 🌤️ weather (Optional)
**Purpose:** Weather data  
**Tools:** Current weather, forecasts  
**Free Tier:** 60 calls/min  
**Setup:** Requires WEATHER_API_KEY (OpenWeatherMap)  

**Example Usage:**
```
What's the weather in Huber Heights, OH?
Get 7-day forecast for Dayton
```

---

## 🎯 Recommended Configuration

### For RuneScape Trading (Your Use Case)

**Essential:**
- ✅ runescape (game data - essential)
- ✅ sequential-thinking (strategy development)
- ✅ memory (remember portfolios, strategies)
- ✅ sqlite (store trading history)
- ✅ filesystem (save reports, configs)

**Recommended:**
- ✅ fetch (research items, guides)
- ✅ puppeteer (web automation)
- ✅ brave-search (web research - get free API key)

**Optional:**
- ⏸️ github (only if managing code repos)
- ⏸️ weather (not relevant for trading)

### For General Development

**Enable:**
- ✅ filesystem
- ✅ git
- ✅ memory
- ✅ sqlite
- ✅ sequential-thinking
- ✅ fetch
- ✅ puppeteer
- ✅ brave-search
- ✅ github (if you code)

### For Productivity & Research

**Enable:**
- ✅ sequential-thinking (problem-solving)
- ✅ memory (knowledge management)
- ✅ fetch (web research)
- ✅ brave-search (web search)
- ✅ time (scheduling)
- ✅ puppeteer (automation)

---

### For General Development

**Enable:**
- ✅ filesystem
- ✅ git
- ✅ memory
- ✅ fetch
- ✅ brave-search
- ✅ github (if you code)

---

## 🔧 Troubleshooting

### Server Not Loading

1. **Check LM Studio version:** Must be 0.2.20+
2. **Restart LM Studio:** After config changes
3. **Check paths:** Ensure paths are correct for your system
4. **Check permissions:** Ensure files are executable

### API Key Issues

1. **Verify key:** Double-check API key is correct
2. **Check tier:** Ensure you're within free tier limits
3. **Restart:** Restart LM Studio after adding keys

### Tool Not Available

1. **Check disabled flag:** Ensure `disabled: false`
2. **Check server status:** Server must be running
3. **Restart LM Studio:** Sometimes needed after config changes

---

## 📊 Server Status

Check server status in LM Studio:
1. Open LM Studio
2. Go to Settings → MCP Servers
3. Check status indicators (green = connected)

---

## 🎓 Best Practices

### 1. Start Minimal
Enable only what you need:
```json
{
  "runescape": { "disabled": false },
  "filesystem": { "disabled": false },
  "memory": { "disabled": false }
}
```

### 2. Add Gradually
Add servers as you need them:
```json
// Add when you need web search
"brave-search": { "disabled": false }

// Add when you need GitHub
"github": { "disabled": false }
```

### 3. Secure API Keys
- Never commit API keys to git
- Use environment variables
- Rotate keys periodically

### 4. Monitor Usage
- Check API dashboards for usage
- Stay within free tier limits
- Upgrade if needed

---

## 📚 Resources

- **MCP Protocol:** https://modelcontextprotocol.io/
- **MCP Servers:** https://github.com/modelcontextprotocol/servers
- **Awesome MCP:** https://github.com/wong2/awesome-mcp-servers
- **PulseMCP:** https://www.pulsemcp.com/servers
- **Brave Search API:** https://brave.com/search/api/
- **OpenWeather API:** https://openweathermap.org/api
- **GitHub Tokens:** https://github.com/settings/tokens

---

**Last Updated:** March 17, 2026  
**Version:** 2.0.1  
**Maintained by:** DuckBot
