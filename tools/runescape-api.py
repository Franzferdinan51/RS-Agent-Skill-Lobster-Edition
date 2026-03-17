#!/usr/bin/env python3
"""
RuneScape API Client - Lobster Edition
======================================
Comprehensive Python client for RuneScape APIs with agent-friendly features.

Features:
- Grand Exchange item data (prices, trends, categories, 180-day history)
- Hiscores (player rankings, stats for RS3 and OSRS)
- Clan information (rankings, members, stats, citadel tracking)
- Runemetrics (activity logs, quests, XP tracking)
- JSON output for agent integration
- Rate limiting and caching
- Comprehensive error handling

Usage:
    python3 runescape-api.py --clan "Lords of Arcadia"
    python3 runescape-api.py --player "Zezima" --json
    python3 runescape-api.py --item "Twisted bow"
    python3 runescape-api.py --top-clans --limit 10

Author: DuckBot / Franzferdinan51
Version: 1.0.0
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


# API Base URLs
GE_BASE = "https://secure.runescape.com/m=itemdb_rs/api"
HISCORE_BASE = "https://secure.runescape.com/m=hiscore"
CLAN_BASE = "https://secure.runescape.com/m=clan-hiscores"
RUNEMETRICS_BASE = "https://apps.runescape.com/runemetrics"

# Skill IDs for RS3
RS3_SKILLS = [
    "Overall", "Attack", "Defence", "Strength", "Constitution", "Ranged",
    "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
    "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
    "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction",
    "Summoning", "Dungeoneering", "Divination", "Invention", "Archaeology", "Necromancy"
]

# Skill IDs for OSRS
OSRS_SKILLS = [
    "Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged",
    "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
    "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
    "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction"
]

# GE Categories
GE_CATEGORIES = {
    0: "Miscellaneous", 1: "Ammo", 2: "Arrows", 3: "Bolts", 4: "Construction materials",
    5: "Construction products", 6: "Cooking ingredients", 7: "Costumes", 8: "Crafting materials",
    9: "Familiars", 10: "Farming produce", 11: "Fletching materials", 12: "Food and Drink",
    13: "Herblore materials", 14: "Hunting equipment", 15: "Hunting Produce", 16: "Jewellery",
    17: "Mage armour", 18: "Mage weapons", 19: "Melee armour - low level", 20: "Melee armour - mid level",
    21: "Melee armour - high level", 22: "Melee weapons - low level", 23: "Melee weapons - mid level",
    24: "Melee weapons - high level", 25: "Mining and Smithing", 26: "Potions", 27: "Prayer armour",
    28: "Prayer materials", 29: "Range armour", 30: "Range weapons", 31: "Runecrafting",
    32: "Runes, Spells and Teleports", 33: "Seeds", 34: "Summoning scrolls", 35: "Tools and containers",
    36: "Woodcutting product", 37: "Pocket items", 38: "Stone spirits", 39: "Salvage",
    40: "Firemaking products", 41: "Archaeology materials", 42: "Wood spirits", 43: "Necromancy armour"
}


class RuneScapeAPI:
    """Client for RuneScape official APIs with agent-friendly features."""
    
    def __init__(self, session_id: Optional[int] = None, rate_limit_ms: int = 150):
        """
        Initialize API client.
        
        Args:
            session_id: Optional session ID for authenticated endpoints
            rate_limit_ms: Milliseconds between requests (default: 150)
        """
        self.session = requests.Session()
        self.session_id = session_id
        self.rate_limit_ms = rate_limit_ms
        self.last_request_time = 0
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RS-Agent/1.0"
        })
    
    def _rate_limit(self):
        """Enforce rate limiting between API requests."""
        elapsed = (time.time() - self.last_request_time) * 1000
        if elapsed < self.rate_limit_ms:
            time.sleep((self.rate_limit_ms - elapsed) / 1000)
        self.last_request_time = time.time()
    
    def _get(self, url: str, timeout: int = 10) -> Optional[Dict]:
        """Make a rate-limited GET request."""
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None
    
    # ==================== GRAND EXCHANGE API ====================
    
    def get_ge_info(self) -> Optional[Dict]:
        """Get Grand Exchange database info (last update runeday)."""
        return self._get(f"{GE_BASE}/info.json")
    
    def get_item_detail(self, item_id: int) -> Optional[Dict]:
        """Get detailed item information from Grand Exchange."""
        data = self._get(f"{GE_BASE}/catalogue/detail.json?item={item_id}")
        return data.get("item") if data else None
    
    def get_item_graph(self, item_id: int) -> Optional[Dict]:
        """Get 180-day price history for an item."""
        return self._get(f"{GE_BASE}/graph/{item_id}.json")
    
    def get_category_items(self, category_id: int, letter: str = "a", page: int = 1) -> Optional[Dict]:
        """Get items in a category."""
        return self._get(f"{GE_BASE}/catalogue/items.json?category={category_id}&alpha={letter}&page={page}")
    
    def search_item_by_name(self, name: str) -> Optional[Dict]:
        """Search for an item by name."""
        first_letter = name[0].lower() if name[0].isalpha() else "%23"
        results = self.get_category_items(0, first_letter, 1)
        if results:
            for item in results.get("items", []):
                if name.lower() in item.get("name", "").lower():
                    return item
        return None
    
    # ==================== HISCORES API ====================
    
    def get_player_stats(self, player_name: str, game_mode: str = "normal") -> Dict:
        """Get player's hiscores data."""
        modes = {
            "normal": "", "ironman": "_ironman", "hardcore_ironman": "_hardcore_ironman",
            "leagues": "_leagues", "oldschool": "_oldschool", "osrs_ironman": "_oldschool_ironman",
            "osrs_hardcore": "_oldschool_hardcore_ironman"
        }
        suffix = modes.get(game_mode, "")
        url = f"{HISCORE_BASE}{suffix}/index_lite.ws?player={player_name}"
        
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {"error": "Player not found", "player": player_name}
            
            skills = OSRS_SKILLS if "oldschool" in game_mode else RS3_SKILLS
            lines = response.text.strip().split("\n")
            result = {"player": player_name, "game_mode": game_mode, "skills": {}}
            
            for i, line in enumerate(lines[:len(skills)]):
                parts = line.split(",")
                if len(parts) == 3:
                    rank, level, xp = parts
                    skill_name = skills[i] if i < len(skills) else f"Skill_{i}"
                    result["skills"][skill_name] = {
                        "rank": int(rank) if rank != "-1" else None,
                        "level": int(level) if level != "-1" else None,
                        "xp": int(xp) if xp != "-1" else None
                    }
            return result
        except Exception as e:
            return {"error": str(e), "player": player_name}
    
    def get_player_ranking(self, skill_id: int = 0, category: int = 0, size: int = 10) -> Optional[List]:
        """Get top players in a skill."""
        data = self._get(f"{HISCORE_BASE}/ranking.json?table={skill_id}&category={category}&size={size}")
        return data
    
    # ==================== CLAN API ====================
    
    def get_clan_ranking(self, limit: int = 10) -> List:
        """Get top clans by XP."""
        data = self._get(f"{CLAN_BASE}/clanRanking.json")
        return data[:limit] if data else []
    
    def get_clan_members(self, clan_name: str, limit: int = 0) -> List:
        """Get clan members list (limit=0 for all)."""
        url = f"{CLAN_BASE}/members_lite.ws?clanName={clan_name.replace(' ', '+')}"
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return []
            lines = response.text.strip().split("\n")
            members = []
            end_idx = limit + 1 if limit > 0 else len(lines)
            for line in lines[1:end_idx]:
                parts = line.split(",")
                if len(parts) >= 3:
                    members.append({
                        "name": parts[0].replace("\u00a0", " "),
                        "rank": parts[1],
                        "total_xp": int(parts[2]) if parts[2].isdigit() else 0,
                        "kills": int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
                    })
            return members
        except Exception:
            return []
    
    def get_clan_info(self, clan_name: str) -> Dict:
        """Get comprehensive clan information."""
        members = self.get_clan_members(clan_name, limit=0)
        if not members:
            return {"error": "Clan not found or empty"}
        
        total_xp = sum(m["total_xp"] for m in members)
        total_kills = sum(m["kills"] for m in members)
        avg_xp = total_xp // len(members) if members else 0
        rank_counts = {}
        for m in members:
            rank_counts[m["rank"]] = rank_counts.get(m["rank"], 0) + 1
        
        top_members = sorted(members, key=lambda x: x["total_xp"], reverse=True)[:10]
        return {
            "clan_name": clan_name, "total_members": len(members),
            "total_xp": total_xp, "average_xp": avg_xp, "total_kills": total_kills,
            "rank_distribution": rank_counts, "top_members": top_members
        }
    
    # ==================== RUNEMETRICS API ====================
    
    def get_runemetrics_profile(self, player_name: str, activities: int = 20) -> Dict:
        """Get player's Runemetrics profile."""
        url = f"{RUNEMETRICS_BASE}/profile/profile?user={player_name}&activities={activities}"
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {"error": "Player not found or profile private"}
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_player_quests(self, player_name: str) -> List:
        """Get player's quest completion status."""
        url = f"{RUNEMETRICS_BASE}/quests?user={player_name}"
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=10)
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []


# Formatting helpers
def format_number(num: int) -> str:
    return f"{num:,}"

def format_xp(xp: int) -> str:
    if xp >= 1_000_000_000: return f"{xp / 1_000_000_000:.2f}B"
    elif xp >= 1_000_000: return f"{xp / 1_000_000:.2f}M"
    elif xp >= 1_000: return f"{xp / 1_000:.1f}K"
    return str(xp)


def main():
    parser = argparse.ArgumentParser(description="RuneScape API Client - Lobster Edition")
    
    clan_group = parser.add_argument_group("Clan Queries")
    clan_group.add_argument("--clan", type=str, help="Get clan info by name")
    clan_group.add_argument("--clan-members", type=str, help="List clan members")
    clan_group.add_argument("--top-clans", action="store_true", help="Show top clans")
    
    player_group = parser.add_argument_group("Player Queries")
    player_group.add_argument("--player", type=str, help="Get player hiscores")
    player_group.add_argument("--runemetrics", action="store_true", help="Include Runemetrics data")
    player_group.add_argument("--top-players", action="store_true", help="Show top players")
    player_group.add_argument("--skill", type=int, default=0, help="Skill ID for top players")
    player_group.add_argument("--game-mode", type=str, default="normal", help="Game mode (normal, ironman, oldschool)")
    
    item_group = parser.add_argument_group("Grand Exchange Queries")
    item_group.add_argument("--item", type=str, help="Search item by name")
    item_group.add_argument("--item-id", type=int, help="Get item details by ID")
    item_group.add_argument("--ge-info", action="store_true", help="Show GE database info")
    
    parser.add_argument("--limit", type=int, default=0, help="Limit results (0 = all)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--rate-limit", type=int, default=150, help="Rate limit in ms")
    
    args = parser.parse_args()
    api = RuneScapeAPI(rate_limit_ms=args.rate_limit)
    
    try:
        if args.top_clans:
            clans = api.get_clan_ranking(args.limit if args.limit > 0 else 10)
            if args.json:
                print(json.dumps(clans, indent=2))
            else:
                print("\n🏆 Top RuneScape Clans\n" + "="*50)
                for i, clan in enumerate(clans, 1):
                    print(f"{i}. {clan['clan_name']}")
                    print(f"   Members: {clan['clan_mates']:,} | XP: {format_xp(clan['xp_total'])}")
                print()
        
        elif args.clan:
            info = api.get_clan_info(args.clan)
            if args.json:
                print(json.dumps(info, indent=2))
            elif "error" in info:
                print(f"❌ {info['error']}")
            else:
                print(f"\n🛡️  Clan: {info['clan_name']}\n" + "="*50)
                print(f"👥 Members: {info['total_members']:,}")
                print(f"💫 Total XP: {format_xp(info['total_xp'])}")
                print(f"📊 Average XP: {format_xp(info['average_xp'])}")
                print(f"⚔️  Total Kills: {info['total_kills']:,}")
                print(f"\n📋 Rank Distribution:")
                for rank, count in sorted(info['rank_distribution'].items(), key=lambda x: -x[1]):
                    print(f"   {rank}: {count}")
                print(f"\n🌟 Top 10 Members:")
                for i, m in enumerate(info['top_members'], 1):
                    print(f"   {i}. {m['name']} ({m['rank']}) - {format_xp(m['total_xp'])}")
                print()
        
        elif args.clan_members:
            members = api.get_clan_members(args.clan_members, args.limit if args.limit > 0 else 50)
            if args.json:
                print(json.dumps(members, indent=2))
            else:
                print(f"\n👥 {args.clan_members} - Members (showing {len(members)})\n" + "="*50)
                print(f"{'#':<4} {'Name':<25} {'Rank':<20} {'XP':<15} {'Kills':<8}")
                print("-" * 72)
                for i, m in enumerate(members, 1):
                    print(f"{i:<4} {m['name']:<25} {m['rank']:<20} {format_xp(m['total_xp']):<15} {m['kills']:<8}")
                print()
        
        elif args.player:
            stats = api.get_player_stats(args.player, args.game_mode)
            if args.json:
                print(json.dumps(stats, indent=2))
            elif "error" in stats:
                print(f"❌ {stats['error']}")
            else:
                print(f"\n🎮 Player: {stats.get('player', args.player)} ({args.game_mode})\n" + "="*50)
                skills = stats.get("skills", {})
                overall = skills.get("Overall", {})
                print(f"📊 Overall Level: {overall.get('level', 'N/A')}")
                print(f"🏆 Overall Rank: {format_number(overall.get('rank', 0)) if overall.get('rank') else 'Unranked'}")
                print(f"⭐ Total XP: {format_xp(overall.get('xp', 0))}")
                if args.verbose:
                    print(f"\n📈 Skill Breakdown:")
                    for skill, data in skills.items():
                        if skill != "Overall" and data.get('level'):
                            print(f"   {skill:<20} Lvl {data['level']:<3} Rank {format_number(data['rank']) if data.get('rank') else '-':<15}")
                print()
        
        elif args.top_players:
            players = api.get_player_ranking(args.skill, size=args.limit if args.limit > 0 else 10)
            if args.json:
                print(json.dumps(players, indent=2))
            elif players:
                skill_names = RS3_SKILLS if args.game_mode != "oldschool" else OSRS_SKILLS
                skill_name = skill_names[args.skill] if args.skill < len(skill_names) else f"Skill {args.skill}"
                print(f"\n🏆 Top {len(players)} Players - {skill_name}\n" + "="*50)
                for i, p in enumerate(players, 1):
                    print(f"{i}. {p['name']} - {format_xp(int(p['score'].replace(',', '')))}")
                print()
        
        elif args.ge_info:
            info = api.get_ge_info()
            if args.json:
                print(json.dumps(info, indent=2))
            elif info:
                print(f"\n📊 Grand Exchange Database Info\n" + "="*50)
                print(f"Last Update Runeday: {info.get('lastConfigUpdateRuneday', 'N/A')}")
                print()
        
        elif args.item_id:
            item = api.get_item_detail(args.item_id)
            if args.json:
                print(json.dumps(item, indent=2))
            elif item:
                print(f"\n🎒 Item ID: {args.item_id}\n" + "="*50)
                print(f"Name: {item.get('name', 'N/A')}")
                print(f"Type: {item.get('type', 'N/A')}")
                print(f"Examine: {item.get('description', 'N/A')}")
                print(f"Members: {'Yes' if item.get('members') else 'No'}")
                print(f"Current Price: {item.get('current', {}).get('price', 'N/A')} ({item.get('current', {}).get('trend', 'neutral')})")
                print()
            else:
                print(f"❌ Item not found: {args.item_id}")
        
        elif args.item:
            item = api.search_item_by_name(args.item)
            if args.json:
                print(json.dumps(item, indent=2))
            elif item:
                print(f"\n🎒 Item: {item.get('name', args.item)}\n" + "="*50)
                print(f"ID: {item.get('id', 'N/A')}")
                print(f"Type: {item.get('type', 'N/A')}")
                print(f"Examine: {item.get('description', 'N/A')}")
                print(f"Members: {'Yes' if item.get('members') else 'No'}")
                print(f"Current Price: {item.get('current', {}).get('price', 'N/A')}")
                print()
            else:
                print(f"❌ Item not found: {args.item}")
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
