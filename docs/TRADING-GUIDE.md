# 💰 Complete Trading Guide

Your comprehensive guide to making money on the Grand Exchange.

---

## 🎯 Table of Contents

1. [Beginner's Guide](#beginners-guide)
2. [Flipping Strategies](#flipping-strategies)
3. [Long-Term Investing](#long-term-investing)
4. [Arbitrage Trading](#arbitrage-trading)
5. [Risk Management](#risk-management)
6. [Advanced Techniques](#advanced-techniques)
7. [Common Mistakes](#common-mistakes)
8. [Tools & Resources](#tools--resources)

---

## 📚 Beginner's Guide

### What is Grand Exchange Trading?

The Grand Exchange (GE) is RuneScape's player-driven marketplace where you can:
- **Buy** items from other players
- **Sell** items to other players
- **Profit** from price differences

### The 5% GE Tax

Every sale on the GE is taxed 5%:
```
Sale Price: 1,000,000 gp
GE Tax (5%): 50,000 gp
You Receive: 950,000 gp
```

**Always factor this into your profit calculations!**

### Getting Started

1. **Start Small** - Begin with 1-10M GP
2. **Learn the Market** - Watch prices for a few days
3. **Use Tools** - This toolkit helps analyze opportunities
4. **Be Patient** - Good trades take time
5. **Track Progress** - Use wealth-tracker.py

### Basic Terminology

| Term | Definition |
|------|------------|
| **Flip** | Buy low, sell high |
| **Spread** | Difference between buy and sell price |
| **Margin** | Your profit after tax |
| **Volume** | How many items trade daily |
| **Liquidity** | How easily you can buy/sell |
| **Trend** | Price direction (up/down/stable) |

---

## 🔄 Flipping Strategies

### What is Flipping?

Flipping is buying items at a low price and selling them higher.

### Strategy 1: Basic Flipping

**How it works:**
1. Find items with wide buy/sell spread
2. Buy at current sell price
3. Set sell order higher
4. Wait for sale

**Example:**
```
Item: Dragon scimitar
Buy Price: 60,000 gp
Sell Price: 65,000 gp
GE Tax: 3,250 gp (5%)
Profit: 1,750 gp per item
ROI: 2.9%
```

**Best for:** Beginners, low risk

### Strategy 2: Volume Flipping

**How it works:**
1. Find high-volume items
2. Make small profit per item
3. Trade large quantities
4. Repeat frequently

**Example:**
```
Item: Blood rune
Buy: 500 gp each
Sell: 520 gp each
Tax: 26 gp
Profit: 6 gp per rune
Quantity: 10,000 runes
Total Profit: 60,000 gp
```

**Best for:** Active traders, consistent income

### Strategy 3: Trend Flipping

**How it works:**
1. Identify trending items
2. Buy before price peaks
3. Sell during peak
4. Exit before crash

**Tools:**
```bash
# Find trending items
python3 tools/ge-trends.py

# Analyze price history
python3 tools/runescape-api.py --item-id 21787 --graph
```

**Best for:** Experienced traders, higher risk/reward

---

## 📈 Long-Term Investing

### What is GE Investing?

Buying items to hold for weeks/months expecting price increases.

### Best Items to Invest In

**1. Rare Items**
- Limited supply
- Consistent demand
- Examples: Party hats, Halloween masks

**2. Skilling Supplies**
- Always in demand
- Price increases with updates
- Examples: Bones, hides, ores

**3. Best-in-Slot Gear**
- Meta changes create opportunities
- Examples: Twisted bow, Scythe, Elder maul

**4. New Content Items**
- Buy early when supply is high
- Sell when demand increases
- Examples: New BIS gear, consumables

### Investment Timeline

| Timeline | Strategy | Risk | Return |
|----------|----------|------|--------|
| **1-4 weeks** | Short-term flip | Low | 5-15% |
| **1-3 months** | Medium hold | Medium | 15-40% |
| **3-12 months** | Long invest | High | 40-200%+ |

### When to Sell

**Take profit when:**
- ✅ Reached target price (e.g., +30%)
- ✅ Market shows reversal signs
- ✅ Need liquidity for better opportunity
- ✅ Item meta is changing

**Don't sell when:**
- ❌ Small dip (10-15%)
- ❌ Panic from others
- ❌ No clear reason

---

## 💱 Arbitrage Trading

### What is Arbitrage?

Exploiting price differences between:
- Different items (substitute arbitrage)
- Different time periods (time arbitrage)
- Different markets (cross-market arbitrage)

### Using the Arbitrage Tool

```bash
# Scan for opportunities
python3 tools/ge-arbitrage.py --scan-all

# Filter by minimum profit
python3 tools/ge-arbitrage.py --min-profit 10000 --min-roi 2.0

# Export to JSON
python3 tools/ge-arbitrage.py --output opportunities.json
```

### Example Arbitrage

**Substitute Arbitrage:**
```
Item A (Battlestaff): 15,000 gp
Item B (Elemental staff): 16,500 gp

Buy Item A → Convert → Sell Item B
Profit after tax: 600 gp per item
```

**Time Arbitrage:**
```
Monday: Buy supplies (low demand)
Friday: Sell supplies (high demand)
Profit: 10-20%
```

---

## 🛡️ Risk Management

### The Golden Rules

1. **Never invest more than you can lose**
2. **Diversify** - Don't put all GP in one item
3. **Set stop-losses** - Know when to exit
4. **Take profits** - Don't get greedy
5. **Keep records** - Track all trades

### Position Sizing

**Conservative:**
- Max 20% of wealth in one item
- Keep 50% liquid GP
- Diversify across 5+ items

**Aggressive:**
- Max 40% in one item
- Keep 20% liquid
- 3-4 items total

### Risk Assessment

| Risk Level | Items | Expected Return | Max Loss |
|------------|-------|-----------------|----------|
| **Low** | Stable supplies | 5-15% | 10% |
| **Medium** | Popular gear | 15-40% | 25% |
| **High** | New content | 40-100%+ | 50%+ |

### Red Flags 🚩

**Avoid items with:**
- ❌ Sudden price spikes (manipulation)
- ❌ No trading volume (illiquid)
- ❌ Upcoming nerfs (check updates)
- ❌ Oversupply (new content)
- ❌ You don't understand the item

---

## 🎓 Advanced Techniques

### 1. Market Making

**Strategy:**
- Place both buy and sell orders
- Profit from spread
- Provide liquidity

**Requirements:**
- Large capital (100M+ GP)
- Active monitoring
- Fast execution

### 2. Contrarian Trading

**Strategy:**
- Buy when others panic sell
- Sell when others FOMO buy
- Go against market sentiment

**Example:**
```
Market crashes 30% on rumor
You buy the dip
Rumor proves false
Price recovers +40%
```

### 3. Event Trading

**Strategy:**
- Trade around game updates
- Buy before content releases
- Sell on release (sell the news)

**Events to Watch:**
- New raids/bosses
- Skill updates
- Item rebalances
- Holiday events

### 4. Statistical Analysis

**Tools:**
```bash
# Detect anomalies
python3 tools/anomaly-detector.py

# Analyze trends
python3 tools/market-analyzer.py

# Track spikes
python3 tools/price-spike-alert.py
```

**Metrics:**
- Z-score (deviation from mean)
- Moving averages (7d, 30d, 90d)
- Volume trends
- Price momentum

---

## ❌ Common Mistakes

### 1. Chasing Losses

**Mistake:** Losing 10M, then risking 20M to "make it back"

**Fix:** Accept losses, learn, move on

### 2. FOMO Trading

**Mistake:** Buying because price is pumping

**Fix:** Have a strategy, stick to it

### 3. Ignoring Tax

**Mistake:** Forgetting 5% GE tax

**Fix:** Always calculate: `Profit = Sale - Buy - Tax`

### 4. Overtrading

**Mistake:** Making too many trades, paying too much tax

**Fix:** Quality over quantity

### 5. No Exit Strategy

**Mistake:** Not knowing when to sell

**Fix:** Set target prices BEFORE buying

### 6. Investing in Memes

**Mistake:** Buying because "everyone says so"

**Fix:** Do your own research (DYOR)

### 7. Poor Record Keeping

**Mistake:** Not tracking trades

**Fix:** Use wealth-tracker.py

```bash
python3 tools/wealth-tracker.py --log-trade
```

---

## 🛠️ Tools & Resources

### This Toolkit

```bash
# Price checking
python3 tools/runescape-api.py --item "Twisted bow"

# Arbitrage scanning
python3 tools/ge-arbitrage.py --scan-all

# Market analysis
python3 tools/market-analyzer.py

# Anomaly detection
python3 tools/anomaly-detector.py

# Wealth tracking
python3 tools/wealth-tracker.py

# Price alerts
python3 tools/price-alert.py --item "Twisted bow" --threshold 300000000
```

### External Resources

- **GE Tracker** - Real-time price tracking
- **RuneLite** - In-game price overlays
- **OSRS Exchange** - Historical data
- **Reddit r/2007scape** - Market sentiment

### Discord Bot

```
/rs-item item:Twisted bow
/rs-price-alert item:Twisted bow threshold:300000000
/rs-market-analyzer
```

---

## 📊 Example Trades

### Trade 1: Safe Flip

```
Item: Dragon bones
Buy: 3,000 gp
Sell: 3,200 gp
Tax: 160 gp
Profit: 40 gp
Quantity: 10,000
Total Profit: 400,000 gp
Time: 2 days
Risk: Low ✅
```

### Trade 2: Medium Risk

```
Item: Twisted bow
Buy: 290,000,000 gp
Sell: 310,000,000 gp
Tax: 15,500,000 gp
Profit: 4,500,000 gp
ROI: 1.55%
Time: 1 week
Risk: Medium ⚠️
```

### Trade 3: High Risk Investment

```
Item: New raid gear
Buy: 50,000,000 gp (release day)
Sell: 80,000,000 gp (2 months later)
Tax: 4,000,000 gp
Profit: 26,000,000 gp
ROI: 52%
Time: 2 months
Risk: High 🔴
```

---

## 🎯 Profit Goals

### Realistic Expectations

| Capital | Daily Goal | Weekly Goal | Monthly Goal |
|---------|------------|-------------|--------------|
| **1M GP** | 50K (5%) | 350K | 1.5M |
| **10M GP** | 500K (5%) | 3.5M | 15M |
| **100M GP** | 5M (5%) | 35M | 150M |
| **1B GP** | 50M (5%) | 350M | 1.5B |

**Note:** 5% daily is VERY ambitious. More realistic:
- 1-2% daily for active flippers
- 5-10% weekly for swing traders
- 20-50% monthly for investors

---

## 📚 Continue Learning

### Next Steps

1. **Practice** - Start with small amounts
2. **Track** - Log every trade
3. **Analyze** - Review what worked/didn't
4. **Learn** - Read more guides
5. **Community** - Join trading discords

### Advanced Reading

- [`EXAMPLES.md`](EXAMPLES.md) - Code examples
- [`AGENT-FIRST.md`](AGENT-FIRST.md) - Agent trading patterns
- [`discord-bot/README.md`](discord-bot/README.md) - Discord bot commands

---

**Disclaimer:** Trading involves risk. You can lose money. Never invest more than you can afford to lose. This guide is for educational purposes only.

**Version:** 1.0.0  
**Last Updated:** March 17, 2026  
**Author:** DuckBot / Franzferdinan51
