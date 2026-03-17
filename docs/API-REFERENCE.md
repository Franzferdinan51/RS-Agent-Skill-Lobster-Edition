# RuneScape API Reference

Complete reference for all RuneScape API endpoints used in this project.

---

## 📡 Grand Exchange API

**Base URL:** `https://secure.runescape.com/m=itemdb_rs/api`

### Info Endpoint
```
GET /info.json
```
Returns the last update runeday of the Grand Exchange database.

**Response:**
```json
{"lastConfigUpdateRuneday": 8784}
```

### Item Detail
```
GET /catalogue/detail.json?item={item_id}
```
Get detailed information about a specific item.

**Response:**
```json
{
  "item": {
    "id": 21787,
    "name": "Steadfast boots",
    "description": "A pair of powerful-looking boots.",
    "type": "Miscellaneous",
    "members": true,
    "current": {"trend": "neutral", "price": "5.2m"},
    "today": {"trend": "neutral", "price": 0},
    "day30": {"trend": "negative", "change": "-2.0%"}
  }
}
```

### Price History (180 days)
```
GET /graph/{item_id}.json
```
Get 180-day price history graph data.

**Response:**
```json
{
  "daily": {"1419897600000": 15633853, ...},
  "average": {"1419897600000": 14708793, ...}
}
```

### Category Items
```
GET /catalogue/items.json?category={cat_id}&alpha={letter}&page={page}
```
Get items in a category filtered by first letter.

**Categories:**
| ID | Category | ID | Category |
|----|----------|----|----------|
| 0 | Miscellaneous | 22 | Melee weapons - low level |
| 1 | Ammo | 23 | Melee weapons - mid level |
| 2 | Arrows | 24 | Melee weapons - high level |
| 3 | Bolts | 25 | Mining and Smithing |
| 4 | Construction materials | 26 | Potions |
| 5 | Construction products | 27 | Prayer armour |
| 6 | Cooking ingredients | 28 | Prayer materials |
| 7 | Costumes | 29 | Range armour |
| 8 | Crafting materials | 30 | Range weapons |
| 9 | Familiars | 31 | Runecrafting |
| 10 | Farming produce | 32 | Runes, Spells and Teleports |
| 11 | Fletching materials | 33 | Seeds |
| 12 | Food and Drink | 34 | Summoning scrolls |
| 13 | Herblore materials | 35 | Tools and containers |
| 14 | Hunting equipment | 36 | Woodcutting product |
| 15 | Hunting Produce | 37 | Pocket items |
| 16 | Jewellery | 38 | Stone spirits |
| 17 | Mage armour | 39 | Salvage |
| 18 | Mage weapons | 40 | Firemaking products |
| 19 | Melee armour - low level | 41 | Archaeology materials |
| 20 | Melee armour - mid level | 42 | Wood spirits |
| 21 | Melee armour - high level | 43 | Necromancy armour |

---

## 📊 Hiscores API

**Base URL (RS3):** `https://secure.runescape.com/m=hiscore`  
**Base URL (OSRS):** `https://secure.runescape.com/m=hiscore_oldschool`

### Player Stats
```
GET /index_lite.ws?player={player_name}
```
Get player's skill levels, ranks, and XP.

**Response (CSV format):**
```
55,2736,5400000000
493,99,200000000
966,99,200000000
...
```
Each line: `rank,level,xp`

**Skill Order (RS3):**
1. Overall
2. Attack
3. Defence
4. Strength
5. Constitution
6. Ranged
7. Prayer
8. Magic
9. Cooking
10. Woodcutting
11. Fletching
12. Fishing
13. Firemaking
14. Crafting
15. Smithing
16. Mining
17. Herblore
18. Agility
19. Thieving
20. Slayer
21. Farming
22. Runecrafting
23. Hunter
24. Construction
25. Summoning
26. Dungeoneering
27. Divination
28. Invention
29. Archaeology
30. Necromancy

### Top Players
```
GET /ranking.json?table={skill_id}&category={category}&size={count}
```
Get top players in a skill (max 50).

**Response:**
```json
[
  {"name": "Elfinlocks", "score": "200,000,000", "rank": "1"},
  {"name": "Cow1337killr", "score": "200,000,000", "rank": "2"}
]
```

### Game Mode Variants
- Normal: `/m=hiscore/`
- Ironman: `/m=hiscore_ironman/`
- Hardcore Ironman: `/m=hiscore_hardcore_ironman/`
- Leagues: `/m=hiscore_leagues/`
- OSRS: `/m=hiscore_oldschool/`
- OSRS Ironman: `/m=hiscore_oldschool_ironman/`

---

## 🏰 Clan API

**Base URL:** `https://secure.runescape.com/m=clan-hiscores`

### Top Clans
```
GET /clanRanking.json
```
Get top clans by total XP.

**Response:**
```json
[
  {"rank": 1, "clan_name": "Efficiency Experts", "clan_mates": 499, "xp_total": 1345292298455}
]
```

### Clan Members
```
GET /members_lite.ws?clanName={clan_name}
```
Get all clan members with ranks and XP.

**Response (CSV format):**
```
Clanmate, Clan Rank, Total XP, Kills
cryptosteve2,Owner,105241512,0
Zephryl,Deputy Owner,2347379609,0
...
```

---

## 📜 Runemetrics API

**Base URL:** `https://apps.runescape.com/runemetrics`

### Player Profile
```
GET /profile/profile?user={player_name}&activities={count}
```
Get player profile with skills and activity log.

**Response:**
```json
{
  "name": "Zezima",
  "rank": "6,264",
  "totalskill": 3200,
  "totalxp": 5710000000,
  "combatlevel": 152,
  "questscomplete": 356,
  "activities": [
    {"date": "17-Mar-2026 17:52", "text": "I killed 16 Chaos Elementals."}
  ],
  "skillvalues": [{"id": 27, "level": 120, "xp": 2000000000, "rank": 20741}]
}
```

### Quest Completion
```
GET /quests?user={player_name}
```
Get player's quest completion status.

**Response:**
```json
[
  {"title": "Cook's Assistant", "status": "COMPLETED", "difficulty": 1, "members": false, "questPoints": 1}
]
```

### Monthly XP Gains
```
GET /xp-monthly?searchName={player_name}&skillid={skill_id}
```
Get XP gained in last 12 months for a skill.

---

## ⚠️ Important Notes

### CORS
Most RuneScape APIs do **not** support CORS. You must make requests from backend/server-side code, not browser frontend.

### Rate Limiting
- Official APIs have request throttling
- Recommended: 150-200ms between requests
- Excessive requests may result in temporary blocks

### Authentication
Most endpoints are public. Some require authentication:
- `userRanking` - Requires session ID
- `playerFriendsDetails` - Requires logged-in session

### Player Names
- Case-insensitive for hiscores
- Spaces should be URL-encoded or use `+`
- Special characters may need encoding

---

## 🛠️ Example Requests

### cURL Examples

```bash
# Get clan members
curl "https://secure.runescape.com/m=clan-hiscores/members_lite.ws?clanName=Lords+of+Arcadia"

# Get player stats
curl "https://secure.runescape.com/m=hiscore/index_lite.ws?player=Zezima"

# Get item detail
curl "https://secure.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item=21787"

# Get Runemetrics profile
curl "https://apps.runescape.com/runemetrics/profile/profile?user=Zezima&activities=10"
```

### Python Examples

```python
import requests

# Get clan info
members = requests.get("https://secure.runescape.com/m=clan-hiscores/members_lite.ws?clanName=Lords+of+Arcadia")

# Get player stats
stats = requests.get("https://secure.runescape.com/m=hiscore/index_lite.ws?player=Zezima")

# Parse CSV
for line in stats.text.strip().split("\n"):
    rank, level, xp = line.split(",")
    print(f"Rank: {rank}, Level: {level}, XP: {xp}")
```

---

**Last Updated:** March 17, 2026  
**Version:** 1.0.0  
**Maintained by:** DuckBot / Franzferdinan51
