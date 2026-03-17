#!/usr/bin/env python3
"""
RS3 & OSRS Hiscores Tool - Lobster Edition
==========================================
Lookup player hiscores for both RS3 and OSRS.

Cross-platform: Windows/Linux/macOS compatible

Usage:
    python3 tools/osrs-hiscores.py --player "Zezima" --game osrs
    python3 tools/osrs-hiscores.py --player "Zezima" --game rs3
    python3 tools/osrs-hiscores.py --player "Zezima" --json
"""

import argparse
import json
import sys

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

# Both RS3 and OSRS hiscores
RS3_HISCORES = "https://secure.runescape.com/m=hiscore"
OSRS_HISCORES = "https://secure.runescape.com/m=hiscore_oldschool"

RS3_SKILLS = [
    "Overall", "Attack", "Defence", "Strength", "Constitution", "Ranged",
    "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
    "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
    "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction",
    "Summoning", "Dungeoneering", "Divination", "Invention", "Archaeology", "Necromancy"
]

OSRS_SKILLS = [
    "Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged",
    "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
    "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
    "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction"
]

OSRS_ACTIVITIES = [
    "League Points", "Deadman Points", "Bounty Hunter - Hunter",
    "Bounty Hunter - Rogue", "Clue Scrolls (all)", "Clue Scrolls (beginner)",
    "Clue Scrolls (easy)", "Clue Scrolls (medium)", "Clue Scrolls (hard)",
    "Clue Scrolls (elite)", "Clue Scrolls (master)", "LMS - Rank",
    "PvP Arena - Rank", "Soul Wars Zeal", "Rifts closed", "Colosseum Glory",
    "Collections Logged", "Abyssal Sire", "Alchemical Hydra", "Barrows Chests",
    "Bryophyta", "Callisto", "Calvarion", "Cerberus", "Chambers of Xeric",
    "Chambers of Xeric: Challenge Mode", "Chaos Elemental", "Chaos Fanatic",
    "Commander Zilyana", "Corporeal Beast", "Crazy Archaeologist",
    "Dagannoth Prime", "Dagannoth Rex", "Dagannoth Supreme", "Deranged Archaeologist",
    "Duke Sucellus", "General Graardor", "Giant Mole", "Grotesque Guardians",
    "Hespori", "Kalphite Queen", "King Black Dragon", "Kraken", "Kree'Arra",
    "K'ril Tsutsaroth", "Lunar Chests", "Mimic", "Nex", "Nightmare",
    "Phosani's Nightmare", "Obor", "Phantom Muspah", "Sarachnis", "Scorpia",
    "Scurrius", "Skotizo", "Sol Heredit", "Tempoross", "The Gauntlet",
    "The Corrupted Gauntlet", "The Hueycoatl", "The Leviathan", "The Royal Titans",
    "The Whisperer", "Theatre of Blood", "Theatre of Blood: Hard Mode",
    "Thermonuclear Smoke Devil", "Tombs of Amascut", "Tombs of Amascut: Expert Mode",
    "TzKal-Zuk", "TzTok-Jad", "Vardorvis", "Venenatis", "Vet'ion", "Vorkath",
    "Wintertodt", "Yama", "Zalcano", "Zulrah"
]


def get_hiscores(player_name: str, game: str = "rs3") -> dict:
    """Get hiscores for a player (RS3 or OSRS)."""
    hiscores_url = RS3_HISCORES if game.lower() == "rs3" else OSRS_HISCORES
    skills_list = RS3_SKILLS if game.lower() == "rs3" else OSRS_SKILLS
    
    url = f"{hiscores_url}/index_lite.ws?player={player_name}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code != 200:
            return {"error": "Player not found", "player": player_name, "game": game.upper()}
        
        lines = response.text.strip().split("\n")
        result = {"player": player_name, "game": game.upper(), "skills": {}}
        
        # Parse skills
        for i, line in enumerate(lines[:len(skills_list)]):
            parts = line.split(",")
            if len(parts) == 3:
                rank, level, xp = parts
                skill_name = skills_list[i] if i < len(skills_list) else f"Skill_{i}"
                result["skills"][skill_name] = {
                    "rank": int(rank) if rank != "-1" else None,
                    "level": int(level) if level != "-1" else None,
                    "xp": int(xp) if xp != "-1" else None
                }
        
        return result
    except Exception as e:
        return {"error": str(e), "player": player_name, "game": game.upper()}


def format_xp(xp: int) -> str:
    """Format XP with M/B suffixes."""
    if xp >= 1_000_000_000:
        return f"{xp / 1_000_000_000:.2f}B"
    elif xp >= 1_000_000:
        return f"{xp / 1_000_000:.2f}M"
    elif xp >= 1_000:
        return f"{xp / 1_000:.1f}K"
    return str(xp)


def main():
    parser = argparse.ArgumentParser(description="RS3 & OSRS Hiscores - Lobster Edition")
    parser.add_argument("--player", type=str, required=True, help="Player name")
    parser.add_argument("--game", type=str, default="rs3", choices=["rs3", "osrs"], help="Game version")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    hiscores = get_hiscores(args.player, args.game)
    
    if args.json:
        print(json.dumps(hiscores, indent=2))
        sys.exit(0)
    
    if "error" in hiscores:
        print(f"\n❌ {hiscores['error']}")
        print(f"\n💡 Tips:")
        print(f"   - Check spelling (case-sensitive)")
        print(f"   - Player may not exist or be unranked")
        print(f"   - Try --game osrs or --game rs3")
        sys.exit(1)
    
    print(f"\n🎮 {hiscores['game']} Hiscores - {args.player}")
    print(f"=" * 60)
    
    if not args.activities:
        print(f"\n📊 Skills")
        print(f"{'-' * 60}")
        skills = hiscores.get("skills", {})
        overall = skills.get("Overall", {})
        print(f"📈 Overall Level: {overall.get('level', 'N/A')}")
        print(f"🏆 Overall Rank: {overall.get('rank', 'Unranked'):,}" if overall.get('rank') else "🏆 Overall Rank: Unranked")
        print(f"⭐ Total XP: {format_xp(overall.get('xp', 0))}")
        
        print(f"\n📋 Skill Breakdown:")
        print(f"{'Skill':<20} {'Level':<8} {'XP':<15} {'Rank':<15}")
        print(f"{'-' * 60}")
        
        for skill, data in skills.items():
            if skill != "Overall" and data.get('level'):
                rank_str = f"{data['rank']:,}" if data.get('rank') else "-"
                print(f"{skill:<20} {data['level']:<8} {format_xp(data.get('xp', 0)):<15} {rank_str:<15}")
    
    if not args.skills and hiscores.get("activities"):
        print(f"\n🏆 Activities")
        print(f"{'-' * 60}")
        activities = hiscores.get("activities", {})
        
        # Show top activities by score
        top_activities = sorted(
            [(k, v) for k, v in activities.items() if v.get('score') and v['score'] > 0],
            key=lambda x: x[1]['score'],
            reverse=True
        )[:10]
        
        if top_activities:
            print(f"{'Activity':<35} {'Score':<15} {'Rank':<15}")
            print(f"{'-' * 60}")
            for name, data in top_activities:
                rank_str = f"{data['rank']:,}" if data.get('rank') else "-"
                print(f"{name:<35} {data['score']:<15} {rank_str:<15}")
    
    print()


if __name__ == "__main__":
    main()
