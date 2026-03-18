# 🤖 LM Studio MCP Servers - STABLE Configuration

**Last Updated:** March 17, 2026  
**Version:** 2.0.5 (BrowserOS + Fixed Fetch)

---

## ⚠️ Important: Many MCP Servers Are Broken

Many official MCP servers have **critical bugs**:
- ❌ `fetch` - Exits after first response
- ❌ `time` - Protocol errors
- ❌ `everything` - Test server only
- ❌ Many others - Unreliable

---

## ✅ STABLE Configuration (Tested & Working)

### Core Servers (Always Enabled)

| Server | Purpose | Status |
|--------|---------|--------|
| **runescape** | RuneScape API (13 tools) | ✅ **WORKING** |
| **browseros** | Browser automation | ✅ **WORKING** (NEW!) |
| **fetch** | Web content fetching | ✅ **WORKING** (FIXED!) |
| **filesystem** | File operations | ✅ **WORKING** |
| **memory** | Knowledge graph | ✅ **WORKING** |

**Start with these 5!** They're stable and cover most use cases.

---

### Optional Servers (Enable One at a Time)

| Server | Purpose | Test First |
|--------|---------|------------|
| **git** | Git operations | Enable if you code |
| **sqlite** | Database queries | Enable if you need DB |
| **sequential-thinking** | Problem-solving | Enable for complex tasks |
| **puppeteer** | Browser automation | Heavy, enable if needed |
| **brave-search** | Web search | Has API key configured |
| **weather** | Weather data | Has API key configured |
| **jina-search** | AI search | Alternative to brave |

**How to Enable:**
1. Edit `/Users/duckets/.lmstudio/mcp.json`
2. Change `"disabled": true` to `"disabled": false`
3. **Restart LM Studio**
4. Test the server
5. If it works, keep it. If not, disable it again.

---

## ❌ Broken Servers (Permanently Disabled)

| Server | Issue | Alternative |
|--------|-------|-------------|
| **time** | Protocol errors | Use LLM's built-in time knowledge |
| **everything** | Test server only | Not for production |

## ✅ Fixed Servers

| Server | Previous Issue | Status |
|--------|----------------|--------|
| **fetch** | Exited after first response | ✅ **FIXED** - Custom implementation |

---

## 🚀 Quick Start

### Step 1: Start Minimal

Your current config has **3 core servers enabled**:
```json
{
  "runescape": { "disabled": false },
  "filesystem": { "disabled": false },
  "memory": { "disabled": false }
}
```

### Step 2: Test Core Servers

In LM Studio, try these queries:
```
Get clan info for Lords of Arcadia
List files in my workspace
What do you remember about my trading strategy?
```

If these work, your core setup is good!

### Step 3: Add Optional Servers (One at a Time)

**Example: Enable git**
```json
"git": {
  "disabled": false
}
```

Then:
1. Restart LM Studio
2. Test: `Show git status`
3. If it works ✅, keep it
4. If it fails ❌, disable it again

---

## 🔧 Troubleshooting

### Server Won't Connect

**Symptoms:**
- Red status indicator
- "Connection failed" errors
- MCP error codes

**Fixes:**
1. **Restart LM Studio** (most common fix)
2. **Check server logs:** `~/.lmstudio/server-logs/`
3. **Disable the problematic server**
4. **Try alternative server**

### Server Works Then Stops

**Common with:** `fetch`, `time`, `everything`

**Fix:**
These servers have **known bugs**. Disable them permanently:
```json
"fetch": { "disabled": true }
```

### All Servers Show Errors

**Likely Cause:** LM Studio MCP bridge issue

**Fixes:**
1. **Restart LM Studio completely** (quit and reopen)
2. **Clear MCP cache:** Delete `~/.lmstudio/mcp-cache/`
3. **Start with minimal config** (just 3 core servers)
4. **Update LM Studio** to latest version

---

## 📊 Current Configuration Summary

**Total Servers:** 10
- ✅ **Core (3):** runescape, filesystem, memory
- ⏸️ **Optional (7):** git, sqlite, sequential-thinking, puppeteer, brave-search, weather, jina-search
- ❌ **Broken (3):** fetch, time, everything (removed from config)

**API Keys Configured:**
- ✅ Brave Search: `BSA5j7E0FgEj-CkoWkC4cCbgnVNg0pr`
- ✅ Weather: `1d4da2d704f66b4c9d5913db8c2179b2`

---

## 🎯 Recommended for RuneScape Trading

**Minimal Setup (Recommended):**
```json
{
  "runescape": { "disabled": false },
  "filesystem": { "disabled": false },
  "memory": { "disabled": false }
}
```

**Enhanced Setup (If Stable):**
```json
{
  "runescape": { "disabled": false },
  "filesystem": { "disabled": false },
  "memory": { "disabled": false },
  "sqlite": { "disabled": false },
  "sequential-thinking": { "disabled": false },
  "brave-search": { "disabled": false }
}
```

**Full Setup (Use at Your Own Risk):**
Enable all optional servers, but be prepared to disable any that cause issues.

---

## 📚 Resources

- **MCP Servers Repo:** https://github.com/modelcontextprotocol/servers
- **Known Issues:** https://github.com/modelcontextprotocol/servers/issues
- **Fetch Issues:** #2464, #2517 (exits after first response)
- **LM Studio Docs:** https://lmstudio.ai/docs

---

## 🆘 Still Having Issues?

1. **Check LM Studio version:** Must be 0.2.20+
2. **Check Node.js version:** Must be 18+
3. **Try alternative MCP host:** Cursor, Claude Desktop
4. **Report bugs:** https://github.com/modelcontextprotocol/servers/issues

---

**Remember:** Start minimal, add slowly, test everything! 🚀

**Last Tested:** March 17, 2026  
**LM Studio Version:** 0.2.20+  
**Status:** ✅ Core servers stable, optional servers vary
