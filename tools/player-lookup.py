#!/usr/bin/env python3
"""
Player Lookup - Lobster Edition
================================
Comprehensive player profile lookup for RuneScape 3 and Old School.

Features:
- RS3 and OSRS hiscores
- Runemetrics activity logs
- Quest completion status
- Skill breakdown
- JSON output for agents

Usage:
    python3 player-lookup.py --player "Zezima"
    python3 player-lookup.py --player "Zezima" --osrs --json
    python3 player-lookup.py --player "Zezima" --full

Author: DuckBot / Franzferdinan51
Version: 1.0.0
"""

import argparse
import json
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

HISCORE_RS3 = "https://secure.runescape.com/m=hiscore"
HISCORE_OSRS = "https://secure.runescape.com/m=hiscore_oldschool"
RUNEMETRICS = "https://apps.runescape.com/runemetrics"

RS3_SKILLS = ["Overall", "Attack", "Defence", "Strength", "Constitution", "Ranged", "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing", "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility", "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction", "Summoning", "Dungeoneering", "Divination", "Invention", "Archaeology", "Necromancy"]

OSRS_SKILLS = ["Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged", "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing", "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility", "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction"]


def get_hiscores(player: str, osrs: bool = False) -> dict:
    """Get player hiscores data."""
    base = HISCORE_OSRS if osrs else HISCORE_RS3
    try:
        response = requests.get(f"{base}/index_lite.ws?player={player}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            return {"error": "Player not found"}
        
        skills = OSRS_SKILLS if osrs else RS3_SKILLS
        lines = response.text.strip().split("\n")
        result = {"player": player, "game": "OSRS" if osrs else "RS3", "skills": {}}
        
        for i, line in enumerate(lines[:len(skills)]):
            parts = line.split(",")
            if len(parts) == 3:
                rank, level, xp = parts
                result["skills"][skills[i]] = {
                    "rank": int(rank) if rank != "-1" else None,
                    "level": int(level) if level != "-1" else None,
                    "xp": int(xp) if xp != "-1" else None
                }
        return result
    except Exception as e:
        return {"error": str(e)}


def get_runemetrics(player: str) -> dict:
    """Get player Runemetrics profile."""
    try:
        response = requests.get(f"{RUNEMETRICS}/profile/profile?user={player}&activities=10", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            return {"error": "Profile private or not found"}
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def format_xp(xp: int) -> str:
    if xp >= 1_000_000_000: return f"{xp / 1_000_000_000:.2f}B"
    elif xp >= 1_000_000: return f"{xp / 1_000_000:.2f}M"
    return f"{xp:,}"


def main():
    parser = argparse.ArgumentParser(description="Player Lookup - Lobster Edition")
    parser.add_argument("--player", type=str, required=True, help="Player name")
    parser.add_argument("--osrs", action="store_true", help="Old School RuneScape")
    parser.add_argument("--full", action="store_true", help="Include Runemetrics and full details")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    print(f"\n🎮 Player Lookup - Lobster Edition")
    print(f"=" * 60)
    print(f"🔍 Searching: {args.player}")
    print(f"=" * 60)
    
    # Get hiscores
    hiscores = get_hiscores(args.player, args.osrs)
    
    if args.json:
        output = {"hiscores": hiscores}
        if args.full:
            output["runemetrics"] = get_runemetrics(args.player)
        print(json.dumps(output, indent=2))
        return
    
    if "error" in hiscores:
        print(f"\n❌ {hiscores['error']}")
        print(f"\n💡 Tips:")
        print(f"   - Check spelling (case-sensitive)")
        print(f"   - Try _ instead of spaces")
        print(f"   - Player may not exist or be unranked")
        return
    
    print(f"\n📊 Hiscores ({hiscores['game']})")
    print(f"{'-' * 60}")
    
    skills = hiscores.get("skills", {})
    overall = skills.get("Overall", {})
    print(f"👤 Player: {args.player}")
    print(f"📈 Overall Level: {overall.get('level', 'N/A')}")
    print(f"🏆 Overall Rank: {overall.get('rank', 'Unranked'):,}" if overall.get('rank') else "🏆 Overall Rank: Unranked")
    print(f"⭐ Total XP: {format_xp(overall.get('xp', 0))}")
    
    if args.full:
        print(f"\n📋 Skill Breakdown")
        print(f"{'-' * 60}")
        print(f"{'Skill':<20} {'Level':<8} {'XP':<15} {'Rank':<15}")
        print(f"{'-' * 60}")
        
        for skill, data in skills.items():
            if skill != "Overall" and data.get('level'):
                rank_str = f"{data['rank']:,}" if data.get('rank') else "-"
                print(f"{skill:<20} {data['level']:<8} {format_xp(data.get('xp', 0)):<15} {rank_str:<15}")
    
    if args.full:
        print(f"\n📜 Runemetrics")
        print(f"{'-' * 60}")
        rm = get_runemetrics(args.player)
        
        if "error" not in rm:
            print(f"⚔️  Combat Level: {rm.get('combatlevel', 'N/A')}")
            print(f"📚 Quests: {rm.get('questscomplete', 0)}/{rm.get('questsstarted', 0)} complete")
            print(f"🌐 Online: {'Yes' if rm.get('loggedIn') == 'true' else 'No'}")
            
            if "activities" in rm and rm["activities"]:
                print(f"\n📝 Recent Activity:")
                for act in rm["activities"][:5]:
                    print(f"   • {act.get('date', 'N/A')}: {act.get('text', 'Unknown')}")
        else:
            print(f"   ❌ {rm['error']}")
    
    print()


if __name__ == "__main__":
    main()
