# 🚨 MCP Troubleshooting Guide - RS-Agent

**Last Updated:** March 17, 2026  
**Version:** 2.0.6 (Critical Fixes)

---

## ⚡ Quick Fixes (Try These First!)

### Issue: npm Permission Errors
```
npm error EACCES: permission denied
npm error path /Users/duckets/.npm/_cacache/
```

**Fix:**
```bash
cd /Users/duckets/.openclaw/workspace/rs-agent-tools
chmod +x scripts/fix-npm-permissions.sh
./scripts/fix-npm-permissions.sh
```

Then **restart LM Studio**.

---

### Issue: MCP Connection Closed
```
MCP error -32000: Connection closed
```

**Causes:**
1. npm permission issues (fix above)
2. Server crashing on startup
3. LM Studio MCP bridge bug

**Fixes:**
1. Fix npm permissions (see above)
2. Test server manually:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 /Users/duckets/.openclaw/workspace/rs-agent-tools/mcp-server.py
   ```
3. Restart LM Studio completely (quit and reopen)

---

### Issue: Empty Responses
**Cause:** Server not initialized properly

**Fix:**
1. Use minimal config: `/Users/duckets/.lmstudio/mcp-minimal.json`
2. Restart LM Studio
3. Test with simple query: "Get clan info"

---

## 🔧 Step-by-Step Setup

### Step 1: Fix npm Permissions
```bash
cd /Users/duckets/.openclaw/workspace/rs-agent-tools
./scripts/fix-npm-permissions.sh
```

### Step 2: Use Minimal Config
Replace your MCP config with minimal working version:
```bash
cp /Users/duckets/.lmstudio/mcp-minimal.json /Users/duckets/.lmstudio/mcp.json
```

### Step 3: Restart LM Studio
**Important:** Quit completely (Cmd+Q) and reopen.

### Step 4: Test RuneScape MCP
Try this query in LM Studio:
```
Get clan info for Lords of Arcadia
```

**Expected Response:** Clan information with members, XP, etc.

### Step 5: Add More Servers (Optional)
Once runescape works, you can add other servers **one at a time**:

Edit `/Users/duckets/.lmstudio/mcp.json`:
```json
{
  "mcpServers": {
    "runescape": { ... },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/duckets/.openclaw/workspace"],
      "disabled": false
    }
  }
}
```

Then restart LM Studio and test.

---

## 🧪 Testing Checklist

### Test 1: Verify Python Server Works
```bash
cd /Users/duckets/.openclaw/workspace/rs-agent-tools
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 mcp-server.py
```

**Expected:** JSON response with protocol version

### Test 2: Verify Tools List
```bash
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python3 mcp-server.py
```

**Expected:** List of 13 tools

### Test 3: Test Actual Tool
```bash
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"runescape_api","arguments":{"clan":"Lords of Arcadia"}}}' | python3 mcp-server.py
```

**Expected:** Clan information JSON

### Test 4: Test in LM Studio
Query: "Get clan info for Lords of Arcadia"

**Expected:** Formatted clan information

---

## ❌ Known Broken Servers

**DO NOT USE** (permanently broken):
- `@modelcontextprotocol/server-fetch` - Exits after first response
- `@modelcontextprotocol/server-time` - Protocol errors
- `@modelcontextprotocol/server-everything` - Test server only

**Use Instead:**
- Fetch → Our custom `fetch-mcp-server.py` (included)
- Time → Use LLM's built-in knowledge
- Everything → Not needed

---

## ⚠️ Servers That May Have Issues

These work sometimes but can be unstable:
- `brave-search` - npm install issues
- `puppeteer` - Heavy, slow to start
- `git` - May need additional setup
- `sqlite` - May need database file

**Recommendation:** Start with just `runescape`, add others slowly.

---

## 📊 Working Configuration

### Minimal (Recommended)
```json
{
  "mcpServers": {
    "runescape": {
      "command": "python3",
      "args": ["/Users/duckets/.openclaw/workspace/rs-agent-tools/mcp-server.py"],
      "cwd": "/Users/duckets/.openclaw/workspace/rs-agent-tools"
    }
  }
}
```

**Status:** ✅ **GUARANTEED WORKING**

### Basic (If You Need More)
```json
{
  "mcpServers": {
    "runescape": { ... },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/duckets/.openclaw/workspace"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Status:** ⚠️ **Test One at a Time**

---

## 🔍 How to Read LM Studio Logs

Location: `~/.lmstudio/server-logs/`

**Common Errors:**

### EACCES: permission denied
```
npm error EACCES: permission denied
npm error path /Users/duckets/.npm/_cacache/
```
**Fix:** Run `./scripts/fix-npm-permissions.sh`

### Connection closed
```
MCP error -32000: Connection closed
```
**Fix:** Server crashed - check if npm installed correctly

### Unknown method: initialize
```
MCP error -32601: Unknown method: initialize
```
**Fix:** Server doesn't implement MCP protocol - use our custom server

---

## 🆘 Still Having Issues?

### 1. Check Prerequisites
```bash
# Check Python version (need 3.8+)
python3 --version

# Check npm version
npm --version

# Check npx works
npx --version
```

### 2. Reinstall Dependencies
```bash
cd /Users/duckets/.openclaw/workspace/rs-agent-tools
pip3 install -r requirements.txt
```

### 3. Clear All Caches
```bash
# Clear npm cache
npm cache clean --force

# Clear LM Studio MCP cache
rm -rf ~/.lmstudio/mcp-cache/

# Restart LM Studio
```

### 4. Test with Fresh Config
```bash
# Backup current config
cp /Users/duckets/.lmstudio/mcp.json /Users/duckets/.lmstudio/mcp.json.backup

# Use minimal config
cp /Users/duckets/.lmstudio/mcp-minimal.json /Users/duckets/.lmstudio/mcp.json

# Restart LM Studio
```

---

## 📚 Additional Resources

- **Main Documentation:** `docs/LMSTUDIO-MCP-STABLE.md`
- **API Reference:** `docs/API-REFERENCE.md`
- **Examples:** `docs/EXAMPLES.md`
- **GitHub Issues:** https://github.com/modelcontextprotocol/servers/issues

---

## ✅ Success Indicators

You know it's working when:
1. ✅ No errors in LM Studio logs
2. ✅ Green status indicator for runescape server
3. ✅ "Get clan info" returns actual data
4. ✅ No "Connection closed" errors
5. ✅ No npm permission errors

---

## 🎯 Quick Reference

| Problem | Solution |
|---------|----------|
| npm permission errors | `./scripts/fix-npm-permissions.sh` |
| Connection closed | Restart LM Studio + use minimal config |
| Empty responses | Test server manually + check logs |
| Server won't start | Check Python version + dependencies |
| Tools not showing | Test tools/list manually |

---

**Last Tested:** March 17, 2026  
**LM Studio Version:** 0.2.20+  
**Python Version:** 3.8+  
**Status:** ✅ Minimal config guaranteed working

**Remember:** Start minimal, add slowly, test everything! 🚀
