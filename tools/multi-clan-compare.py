#!/usr/bin/env python3
"""
Multi-Clan Comparison - Lobster Edition
=======================================
Compare up to 5 clans side-by-side.

Cross-platform: Windows/Linux/macOS compatible

Usage:
    python tools/multi-clan-compare.py --clan "Lords of Arcadia" --clan "Efficiency Experts"
    python tools/multi-clan-compare.py --clan "Clan1" --clan "Clan2" --clan "Clan3" --json
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path

# Cross-platform: Use pathlib for all paths
TOOLS_DIR = Path(__file__).parent


def get_clan_info(clan_name: str) -> dict:
    """Get clan information using runescape-api.py."""
    try:
        # Cross-platform: Use subprocess with proper path handling
        cmd = [sys.executable, str(TOOLS_DIR / "runescape-api.py"), "--clan", clan_name, "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"error": "Failed to get clan info"}
    except Exception as e:
        return {"error": str(e)}


def compare_clans(clan_names: list) -> dict:
    """Compare multiple clans."""
    clans_data = []
    
    for clan_name in clan_names:
        print(f"Fetching data for {clan_name}...", file=sys.stderr)
        data = get_clan_info(clan_name)
        data["clan_name"] = clan_name
        clans_data.append(data)
    
    # Create comparison
    comparison = {
        "clans": clans_data,
        "comparison": {
            "member_counts": [(c.get("clan_name", "Unknown"), c.get("total_members", 0)) for c in clans_data],
            "total_xp": [(c.get("clan_name", "Unknown"), c.get("total_xp", 0)) for c in clans_data],
            "average_xp": [(c.get("clan_name", "Unknown"), c.get("average_xp", 0)) for c in clans_data],
        }
    }
    
    # Determine rankings
    comparison["rankings"] = {
        "most_members": sorted(comparison["comparison"]["member_counts"], key=lambda x: x[1], reverse=True),
        "highest_total_xp": sorted(comparison["comparison"]["total_xp"], key=lambda x: x[1], reverse=True),
        "highest_average_xp": sorted(comparison["comparison"]["average_xp"], key=lambda x: x[1], reverse=True),
    }
    
    return comparison


def format_number(num: int) -> str:
    """Format number with commas."""
    return f"{num:,}"


def main():
    parser = argparse.ArgumentParser(description="Multi-Clan Comparison - Lobster Edition")
    parser.add_argument("--clan", type=str, action="append", required=True, 
                       help="Clan name to compare (can specify multiple)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--output", type=str, help="Export to file (JSON/HTML/Markdown)")
    
    args = parser.parse_args()
    
    if len(args.clan) > 5:
        print("❌ Maximum 5 clans can be compared")
        sys.exit(1)
    
    print(f"\n🛡️  Multi-Clan Comparison")
    print(f"{'=' * 80}")
    print(f"Comparing {len(args.clan)} clans: {', '.join(args.clan)}\n")
    
    comparison = compare_clans(args.clan)
    
    if args.json:
        print(json.dumps(comparison, indent=2))
    else:
        # Text-based comparison table
        clans = comparison["clans"]
        
        print(f"{'Clan':<30} {'Members':<12} {'Total XP':<20} {'Avg XP':<20}")
        print(f"{'-' * 80}")
        
        for clan in clans:
            name = clan.get("clan_name", "Unknown")[:28]
            members = clan.get("total_members", 0)
            total_xp = clan.get("total_xp", 0)
            avg_xp = clan.get("average_xp", 0)
            
            print(f"{name:<30} {members:<12} {format_number(total_xp):<20} {format_number(avg_xp):<20}")
        
        print(f"\n📊 Rankings")
        print(f"{'-' * 80}")
        
        print(f"\nMost Members:")
        for i, (name, count) in enumerate(comparison["rankings"]["most_members"], 1):
            print(f"  {i}. {name}: {count:,}")
        
        print(f"\nHighest Total XP:")
        for i, (name, xp) in enumerate(comparison["rankings"]["highest_total_xp"], 1):
            print(f"  {i}. {name}: {format_number(xp)}")
        
        print(f"\nHighest Average XP:")
        for i, (name, xp) in enumerate(comparison["rankings"]["highest_average_xp"], 1):
            print(f"  {i}. {name}: {format_number(xp)}")
        
        print()
    
    # Export to file
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if args.output.endswith(".json"):
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(comparison, f, indent=2)
        else:
            # Default to JSON for other formats
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(comparison, f, indent=2)
        
        print(f"💾 Exported to: {args.output}")
    
    print()


if __name__ == "__main__":
    main()
