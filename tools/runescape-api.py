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
Version: 1.0.1
"""

import argparse
import html
import json
import re
import sys
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

try:
    import requests
except ImportError:
    print("requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


GE_BASES = {
    "rs3": "https://secure.runescape.com/m=itemdb_rs/api",
    "osrs": "https://secure.runescape.com/m=itemdb_oldschool/api",
}
GE_SEARCH_BASES = {
    "rs3": "https://secure.runescape.com/m=itemdb_rs/results",
    "osrs": "https://secure.runescape.com/m=itemdb_oldschool/results",
}
HISCORE_BASE = "https://secure.runescape.com/m=hiscore"
HISCORE_BASE_OSRS = "https://secure.runescape.com/m=hiscore_oldschool"
CLAN_BASE = "https://secure.runescape.com/m=clan-hiscores"
RUNEMETRICS_BASE = "https://apps.runescape.com/runemetrics"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RS-Agent/1.0"
ITEM_SEARCH_RESULT_RE = re.compile(
    r"<a class='table-item-link' href=\"(?P<href>[^\"]+/viewitem\?obj=(?P<id>\d+))\" title=\"(?P<name>[^\"]+)\""
)


RS3_SKILLS = [
    "Overall", "Attack", "Defence", "Strength", "Constitution", "Ranged",
    "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
    "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
    "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction",
    "Summoning", "Dungeoneering", "Divination", "Invention", "Archaeology", "Necromancy",
]

OSRS_SKILLS = [
    "Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged",
    "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
    "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
    "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction",
]

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
    40: "Firemaking products", 41: "Archaeology materials", 42: "Wood spirits", 43: "Necromancy armour",
}


class RuneScapeAPI:
    """Client for RuneScape official APIs with agent-friendly features."""

    def __init__(self, session_id: Optional[int] = None, rate_limit_ms: int = 150, game: str = "rs3"):
        self.session = requests.Session()
        self.session_id = session_id
        self.rate_limit_ms = rate_limit_ms
        self.last_request_time = 0.0
        self.game = game.lower() if game.lower() in GE_BASES else "rs3"
        self.ge_base = GE_BASES[self.game]
        self.ge_search_base = GE_SEARCH_BASES[self.game]
        self.session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    def _rate_limit(self) -> None:
        """Enforce rate limiting between API requests."""
        elapsed = (time.time() - self.last_request_time) * 1000
        if elapsed < self.rate_limit_ms:
            time.sleep((self.rate_limit_ms - elapsed) / 1000)
        self.last_request_time = time.time()

    def _get(self, url: str, timeout: int = 10) -> Optional[Any]:
        """Make a rate-limited GET request."""
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def get_ge_info(self) -> Optional[Dict[str, Any]]:
        """Get Grand Exchange database info (last update runeday)."""
        return self._get(f"{self.ge_base}/info.json")

    def get_item_detail(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed item information from Grand Exchange."""
        data = self._get(f"{self.ge_base}/catalogue/detail.json?item={item_id}")
        return data.get("item") if isinstance(data, dict) else None

    def get_item_graph(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get 180-day price history for an item."""
        return self._get(f"{self.ge_base}/graph/{item_id}.json")

    def get_category_items(self, category_id: int, letter: str = "a", page: int = 1) -> Optional[Dict[str, Any]]:
        """Get items in a category."""
        return self._get(f"{self.ge_base}/catalogue/items.json?category={category_id}&alpha={letter}&page={page}")

    @staticmethod
    def _normalize_item_name(name: str) -> str:
        """Normalize item names for stable matching."""
        return " ".join(name.casefold().split())

    def _search_item_candidates(self, name: str) -> List[Dict[str, Any]]:
        """Search the official GE results page and extract candidate items."""
        self._rate_limit()
        try:
            response = self.session.get(f"{self.ge_search_base}?query={quote_plus(name)}", timeout=10)
            if response.status_code != 200:
                return []
        except Exception:
            return []

        candidates: List[Dict[str, Any]] = []
        seen_ids = set()
        for match in ITEM_SEARCH_RESULT_RE.finditer(response.text):
            item_id = int(match.group("id"))
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            candidates.append({
                "id": item_id,
                "name": html.unescape(match.group("name")),
                "href": html.unescape(match.group("href")),
            })

        return candidates

    def _pick_best_item_candidate(
        self,
        name: str,
        candidates: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Prefer exact matches, then prefix matches, then broader search hits."""
        if not candidates:
            return None

        normalized_query = self._normalize_item_name(name)

        for candidate in candidates:
            if self._normalize_item_name(candidate["name"]) == normalized_query:
                return candidate

        for candidate in candidates:
            if self._normalize_item_name(candidate["name"]).startswith(normalized_query):
                return candidate

        for candidate in candidates:
            if normalized_query in self._normalize_item_name(candidate["name"]):
                return candidate

        return candidates[0]

    def search_item_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Search for an item by name."""
        candidate = self._pick_best_item_candidate(name, self._search_item_candidates(name))
        if not candidate:
            return None

        item = self.get_item_detail(candidate["id"])
        if item:
            return item

        return {
            "id": candidate["id"],
            "name": candidate["name"],
            "error": "Item found in search results but detail lookup failed",
        }

    def get_player_stats(self, player_name: str, game_mode: str = "normal") -> Dict[str, Any]:
        """Get player's hiscores data."""
        modes = {
            "normal": "",
            "ironman": "_ironman",
            "hardcore_ironman": "_hardcore_ironman",
            "leagues": "_leagues",
            "oldschool": "_oldschool",
            "osrs_ironman": "_oldschool_ironman",
            "osrs_hardcore": "_oldschool_hardcore_ironman",
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
            result: Dict[str, Any] = {"player": player_name, "game_mode": game_mode, "skills": {}}

            for i, line in enumerate(lines[:len(skills)]):
                parts = line.split(",")
                if len(parts) != 3:
                    continue
                rank, level, xp = parts
                skill_name = skills[i] if i < len(skills) else f"Skill_{i}"
                result["skills"][skill_name] = {
                    "rank": int(rank) if rank != "-1" else None,
                    "level": int(level) if level != "-1" else None,
                    "xp": int(xp) if xp != "-1" else None,
                }

            return result
        except Exception as exc:
            return {"error": str(exc), "player": player_name}

    def get_player_ranking(self, skill_id: int = 0, category: int = 0, size: int = 10) -> Optional[List[Any]]:
        """Get top players in a skill."""
        hiscore_base = HISCORE_BASE_OSRS if self.game == "osrs" else HISCORE_BASE
        data = self._get(f"{hiscore_base}/ranking.json?table={skill_id}&category={category}&size={size}")
        return data

    def get_clan_ranking(self, limit: int = 10) -> List[Any]:
        """Get top clans by XP."""
        data = self._get(f"{CLAN_BASE}/clanRanking.json")
        return data[:limit] if data else []

    def get_clan_members(self, clan_name: str, limit: int = 0) -> List[Dict[str, Any]]:
        """Get clan members list (limit=0 for all)."""
        url = f"{CLAN_BASE}/members_lite.ws?clanName={clan_name.replace(' ', '+')}"
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return []

            lines = response.text.strip().split("\n")
            members: List[Dict[str, Any]] = []
            end_idx = limit + 1 if limit > 0 else len(lines)
            for line in lines[1:end_idx]:
                parts = line.split(",")
                if len(parts) < 3:
                    continue
                members.append({
                    "name": parts[0].replace("\u00a0", " "),
                    "rank": parts[1],
                    "total_xp": int(parts[2]) if parts[2].isdigit() else 0,
                    "kills": int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0,
                })
            return members
        except Exception:
            return []

    def get_clan_info(self, clan_name: str) -> Dict[str, Any]:
        """Get comprehensive clan information."""
        members = self.get_clan_members(clan_name, limit=0)
        if not members:
            return {"error": "Clan not found or empty"}

        total_xp = sum(member["total_xp"] for member in members)
        total_kills = sum(member["kills"] for member in members)
        avg_xp = total_xp // len(members) if members else 0
        rank_counts: Dict[str, int] = {}
        for member in members:
            rank_counts[member["rank"]] = rank_counts.get(member["rank"], 0) + 1

        top_members = sorted(members, key=lambda item: item["total_xp"], reverse=True)[:10]
        return {
            "clan_name": clan_name,
            "total_members": len(members),
            "total_xp": total_xp,
            "average_xp": avg_xp,
            "total_kills": total_kills,
            "rank_distribution": rank_counts,
            "top_members": top_members,
        }

    def get_runemetrics_profile(self, player_name: str, activities: int = 20) -> Dict[str, Any]:
        """Get player's Runemetrics profile."""
        url = f"{RUNEMETRICS_BASE}/profile/profile?user={player_name}&activities={activities}"
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {"error": "Player not found or profile private"}
            return response.json()
        except Exception as exc:
            return {"error": str(exc)}

    def get_player_quests(self, player_name: str) -> List[Any]:
        """Get player's quest completion status."""
        url = f"{RUNEMETRICS_BASE}/quests?user={player_name}"
        self._rate_limit()
        try:
            response = self.session.get(url, timeout=10)
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []


def format_number(num: int) -> str:
    return f"{num:,}"


def format_xp(xp: int) -> str:
    if xp >= 1_000_000_000:
        return f"{xp / 1_000_000_000:.2f}B"
    if xp >= 1_000_000:
        return f"{xp / 1_000_000:.2f}M"
    if xp >= 1_000:
        return f"{xp / 1_000:.1f}K"
    return str(xp)


def build_error(message: str, **details: Any) -> Dict[str, Any]:
    """Create a structured JSON-friendly error payload."""
    payload: Dict[str, Any] = {"error": message}
    payload.update(details)
    return payload


def main() -> None:
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

    parser.add_argument("--game", choices=["rs3", "osrs"], default="rs3", help="Game version for GE and hiscore lookups")
    parser.add_argument("--limit", type=int, default=0, help="Limit results (0 = all)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--rate-limit", type=int, default=150, help="Rate limit in ms")

    args = parser.parse_args()
    api = RuneScapeAPI(rate_limit_ms=args.rate_limit, game=args.game)

    try:
        if args.top_clans:
            clans = api.get_clan_ranking(args.limit if args.limit > 0 else 10)
            if args.json:
                print(json.dumps(clans, indent=2))
            else:
                print("\nTop RuneScape Clans\n" + "=" * 50)
                for index, clan in enumerate(clans, 1):
                    print(f"{index}. {clan['clan_name']}")
                    print(f"   Members: {clan['clan_mates']:,} | XP: {format_xp(clan['xp_total'])}")
                print()

        elif args.clan:
            info = api.get_clan_info(args.clan)
            if args.json:
                print(json.dumps(info, indent=2))
            elif "error" in info:
                print(f"ERROR: {info['error']}")
            else:
                print(f"\nClan: {info['clan_name']}\n" + "=" * 50)
                print(f"Members: {info['total_members']:,}")
                print(f"Total XP: {format_xp(info['total_xp'])}")
                print(f"Average XP: {format_xp(info['average_xp'])}")
                print(f"Total Kills: {info['total_kills']:,}")
                print("\nRank Distribution:")
                for rank, count in sorted(info["rank_distribution"].items(), key=lambda item: -item[1]):
                    print(f"   {rank}: {count}")
                print("\nTop 10 Members:")
                for index, member in enumerate(info["top_members"], 1):
                    print(f"   {index}. {member['name']} ({member['rank']}) - {format_xp(member['total_xp'])}")
                print()

        elif args.clan_members:
            members = api.get_clan_members(args.clan_members, args.limit if args.limit > 0 else 50)
            if args.json:
                print(json.dumps(members, indent=2))
            else:
                print(f"\n{args.clan_members} - Members (showing {len(members)})\n" + "=" * 50)
                print(f"{'#':<4} {'Name':<25} {'Rank':<20} {'XP':<15} {'Kills':<8}")
                print("-" * 72)
                for index, member in enumerate(members, 1):
                    print(
                        f"{index:<4} {member['name']:<25} {member['rank']:<20} "
                        f"{format_xp(member['total_xp']):<15} {member['kills']:<8}"
                    )
                print()

        elif args.player:
            game_mode = args.game_mode
            if args.game == "osrs" and game_mode == "normal":
                game_mode = "oldschool"
            stats = api.get_player_stats(args.player, game_mode)
            if args.json:
                print(json.dumps(stats, indent=2))
            elif "error" in stats:
                print(f"ERROR: {stats['error']}")
            else:
                print(f"\nPlayer: {stats.get('player', args.player)} ({game_mode})\n" + "=" * 50)
                skills = stats.get("skills", {})
                overall = skills.get("Overall", {})
                print(f"Overall Level: {overall.get('level', 'N/A')}")
                print(f"Overall Rank: {format_number(overall.get('rank', 0)) if overall.get('rank') else 'Unranked'}")
                print(f"Total XP: {format_xp(overall.get('xp', 0))}")
                if args.verbose:
                    print("\nSkill Breakdown:")
                    for skill, data in skills.items():
                        if skill == "Overall" or not data.get("level"):
                            continue
                        rank = format_number(data["rank"]) if data.get("rank") else "-"
                        print(f"   {skill:<20} Lvl {data['level']:<3} Rank {rank:<15}")
                print()

        elif args.top_players:
            players = api.get_player_ranking(args.skill, size=args.limit if args.limit > 0 else 10)
            if args.json:
                print(json.dumps(players, indent=2))
            elif players:
                skill_names = RS3_SKILLS if args.game != "osrs" else OSRS_SKILLS
                skill_name = skill_names[args.skill] if args.skill < len(skill_names) else f"Skill {args.skill}"
                print(f"\nTop {len(players)} Players - {skill_name}\n" + "=" * 50)
                for index, player in enumerate(players, 1):
                    print(f"{index}. {player['name']} - {format_xp(int(player['score'].replace(',', '')))}")
                print()

        elif args.ge_info:
            info = api.get_ge_info()
            if args.json:
                payload = info if info else build_error("GE info unavailable", game=args.game)
                print(json.dumps(payload, indent=2))
            elif info:
                print("\nGrand Exchange Database Info\n" + "=" * 50)
                print(f"Last Update Runeday: {info.get('lastConfigUpdateRuneday', 'N/A')}")
                print()

        elif args.item_id:
            item = api.get_item_detail(args.item_id)
            if args.json:
                payload = item if item else build_error("Item not found", item_id=args.item_id, game=args.game)
                print(json.dumps(payload, indent=2))
            elif item:
                print(f"\nItem ID: {args.item_id}\n" + "=" * 50)
                print(f"Name: {item.get('name', 'N/A')}")
                print(f"Type: {item.get('type', 'N/A')}")
                print(f"Examine: {item.get('description', 'N/A')}")
                print(f"Members: {'Yes' if item.get('members') else 'No'}")
                current = item.get("current", {})
                print(f"Current Price: {current.get('price', 'N/A')} ({current.get('trend', 'neutral')})")
                print()
            else:
                print(f"ERROR: Item not found: {args.item_id}")

        elif args.item:
            item = api.search_item_by_name(args.item)
            if args.json:
                payload = item if item else build_error("Item not found", query=args.item, game=args.game)
                print(json.dumps(payload, indent=2))
            elif item:
                print(f"\nItem: {item.get('name', args.item)}\n" + "=" * 50)
                print(f"ID: {item.get('id', 'N/A')}")
                print(f"Type: {item.get('type', 'N/A')}")
                print(f"Examine: {item.get('description', 'N/A')}")
                print(f"Members: {'Yes' if item.get('members') else 'No'}")
                print(f"Current Price: {item.get('current', {}).get('price', 'N/A')}")
                print()
            else:
                print(f"ERROR: Item not found: {args.item}")

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
