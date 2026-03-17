#!/usr/bin/env python3
"""
Inactive Member Tracker - Lobster Edition
==========================================
Find clan members who haven't been active for X+ days.

Features:
- Scan all clan members for activity
- Configurable inactivity threshold
- JSON output for agent integration
- Detailed activity breakdown
- Export results

Usage:
    python3 inactive-members.py --days 90
    python3 inactive-members.py --clan "Lords of Arcadia" --output inactive.json
    python3 inactive-members.py --days 30 --all

Author: DuckBot / Franzferdinan51
Version: 1.0.0
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

CLAN_BASE = "https://secure.runescape.com/m=clan-hiscores"
RUNEMETRICS_BASE = "https://apps.runescape.com/runemetrics"
DATE_FORMAT = "%d-%b-%Y %H:%M"


def get_clan_members(clan_name: str) -> List[Dict]:
    """Get all clan member names with XP data."""
    url = f"{CLAN_BASE}/members_lite.ws?clanName={clan_name.replace(' ', '+')}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code != 200:
            return []
        lines = response.text.strip().split("\n")
        members = []
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) >= 3:
                members.append({
                    "name": parts[0].replace("\u00a0", " "),
                    "rank": parts[1],
                    "total_xp": int(parts[2]) if parts[2].isdigit() else 0
                })
        return members
    except Exception:
        return []


def check_player_activity(player_name: str) -> Optional[Dict]:
    """Check player's last activity date from Runemetrics."""
    url = f"{RUNEMETRICS_BASE}/profile/profile?user={player_name}&activities=5"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code != 200:
            return {"player": player_name, "error": "Profile private or not found"}
        
        data = response.json()
        result = {
            "player": player_name, "total_xp": data.get("totalxp", 0),
            "combat_level": data.get("combatlevel", 0), "logged_in": data.get("loggedIn", "false") == "true"
        }
        
        if "activities" in data and len(data["activities"]) > 0:
            try:
                last_activity = data["activities"][0]
                activity_date = datetime.strptime(last_activity["date"], DATE_FORMAT)
                result["last_activity"] = activity_date
                result["last_activity_type"] = last_activity.get("text", "Unknown")
                result["days_inactive"] = (datetime.now() - activity_date).days
            except (ValueError, KeyError):
                pass
        
        if "last_activity" not in result:
            result["error"] = "No activity data available"
        
        return result
    except Exception as e:
        return {"player": player_name, "error": str(e)}


def format_date(dt: Optional[datetime]) -> str:
    return dt.strftime("%b %d, %Y") if dt else "N/A"

def format_xp(xp: int) -> str:
    if xp >= 1_000_000_000: return f"{xp / 1_000_000_000:.2f}B"
    elif xp >= 1_000_000: return f"{xp / 1_000_000:.2f}M"
    elif xp >= 1_000: return f"{xp / 1_000:.1f}K"
    return str(xp)


def main():
    parser = argparse.ArgumentParser(description="Inactive Member Tracker - Lobster Edition")
    parser.add_argument("--days", type=int, default=90, help="Days of inactivity to flag")
    parser.add_argument("--clan", type=str, default="Lords of Arcadia", help="Clan name")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--all", action="store_true", help="Show all members")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--rate-limit", type=int, default=150, help="Rate limit in ms")
    
    args = parser.parse_args()
    cutoff_date = datetime.now() - timedelta(days=args.days)
    
    print(f"\n🔍 Inactive Member Tracker - Lobster Edition")
    print(f"=" * 70)
    print(f"🛡️  Clan: {args.clan}")
    print(f"📅 Checking for inactivity: {args.days}+ days (since {cutoff_date.strftime('%b %d, %Y')})")
    print(f"=" * 70)
    
    print(f"\n📋 Fetching clan member list...")
    members = get_clan_members(args.clan)
    
    if not members:
        print("❌ No clan members found.")
        sys.exit(1)
    
    print(f"👥 Found {len(members)} clan members\n🔍 Checking activity logs...\n")
    
    inactive_members = []
    active_members = []
    error_members = []
    
    for i, member in enumerate(members, 1):
        if args.verbose:
            print(f"[{i}/{len(members)}] {member['name']}...", end=" ", flush=True)
        else:
            print(f"[{i}/{len(members)}] {member['name']}", end="\r", flush=True)
        
        activity = check_player_activity(member["name"])
        if activity:
            activity["clan_rank"] = member["rank"]
            activity["clan_xp"] = member["total_xp"]
            
            if activity.get("error"):
                error_members.append(activity)
            elif activity.get("days_inactive") is not None and activity["days_inactive"] >= args.days:
                inactive_members.append(activity)
            else:
                active_members.append(activity)
            
            if args.verbose:
                status = "⚠️" if activity.get("days_inactive", 0) >= args.days else "✅"
                print(f"{status}")
        
        time.sleep(args.rate_limit / 1000)
    
    if not args.verbose:
        print()
    
    inactive_members.sort(key=lambda x: x.get("days_inactive") or 0, reverse=True)
    
    # Convert datetime to string for JSON
    for m in inactive_members:
        if m.get("last_activity"):
            m["last_activity"] = m["last_activity"].isoformat()
    
    # JSON output
    if args.json:
        output = {
            "clan": args.clan,
            "checked_at": datetime.now().isoformat(),
            "inactivity_threshold_days": args.days,
            "total_members": len(members),
            "inactive_members": inactive_members,
            "active_count": len(active_members),
            "error_count": len(error_members)
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)
    
    print(f"\n{'=' * 70}\n📊 RESULTS\n{'=' * 70}")
    
    if inactive_members:
        print(f"\n⚠️  INACTIVE MEMBERS ({len(inactive_members)} members - {args.days}+ days)")
        print(f"{'-' * 70}")
        print(f"{'#':<4} {'Player':<25} {'Days':<10} {'Last Active':<15} {'Rank':<18} {'XP':<12}")
        print(f"{'-' * 70}")
        
        for i, m in enumerate(inactive_members, 1):
            print(f"{i:<4} {m['player']:<25} {m.get('days_inactive', 'N/A'):<10} {format_date(m.get('last_activity')):<15} {m['clan_rank'][:17]:<18} {format_xp(m['total_xp']):<12}")
    else:
        print(f"\n✅ No members inactive for {args.days}+ days!")
    
    print(f"\n{'=' * 70}\n📈 SUMMARY\n{'=' * 70}")
    print(f"Total clan members: {len(members)}")
    print(f"Active (< {args.days} days): {len(active_members)} ({100*len(active_members)/len(members):.1f}%)")
    print(f"Inactive ({args.days}+ days): {len(inactive_members)} ({100*len(inactive_members)/len(members):.1f}%)")
    print(f"Errors/Unknown: {len(error_members)} ({100*len(error_members)/len(members):.1f}%)")
    
    if args.output:
        output_data = {
            "clan": args.clan, "checked_at": datetime.now().isoformat(),
            "inactivity_threshold_days": args.days, "total_members": len(members),
            "inactive_members": inactive_members
        }
        for m in output_data["inactive_members"]:
            if m.get("last_activity"): m["last_activity"] = m["last_activity"].isoformat()
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")
    
    print()


if __name__ == "__main__":
    main()
