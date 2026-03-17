#!/usr/bin/env python3
"""
Citadel Cap Tracker - Lobster Edition
=====================================
Track clan members who have capped at the clan citadel since a specified date.

Features:
- Scan all clan members for citadel capping activity
- Filter by date range
- JSON output for agent integration
- Progress tracking
- Export results

Usage:
    python3 citadel-cap-tracker.py --since "2026-03-11"
    python3 citadel-cap-tracker.py --clan "Lords of Arcadia" --output caps.json
    python3 citadel-cap-tracker.py --since "2026-03-01" --verbose

Author: DuckBot / Franzferdinan51
Version: 1.0.0
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

CLAN_BASE = "https://secure.runescape.com/m=clan-hiscores"
RUNEMETRICS_BASE = "https://apps.runescape.com/runemetrics"
DATE_FORMAT = "%d-%b-%Y %H:%M"


def get_clan_members(clan_name: str) -> List[str]:
    """Get all clan member names."""
    url = f"{CLAN_BASE}/members_lite.ws?clanName={clan_name.replace(' ', '+')}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code != 200:
            return []
        lines = response.text.strip().split("\n")
        return [line.split(",")[0].replace("\u00a0", " ") for line in lines[1:] if line.split(",")]
    except Exception:
        return []


def check_player_citadel_activity(player_name: str, since_date: datetime) -> Optional[Dict]:
    """Check if a player has capped at clan citadel since specified date."""
    url = f"{RUNEMETRICS_BASE}/profile/profile?user={player_name}&activities=100"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code != 200 or "activities" not in response.json():
            return None
        
        cap_date = None
        visit_date = None
        
        for activity in response.json()["activities"]:
            try:
                activity_date = datetime.strptime(activity["date"], DATE_FORMAT)
            except (ValueError, KeyError):
                continue
            
            if activity_date < since_date:
                continue
            
            text = activity.get("text", "").lower()
            if "capped" in text and "citadel" in text:
                cap_date = activity_date
            elif "visited" in text and "citadel" in text and not cap_date:
                visit_date = activity_date
        
        if cap_date or visit_date:
            return {
                "player": player_name, "cap_date": cap_date, "visit_date": visit_date,
                "total_xp": response.json().get("totalxp", 0),
                "rank": response.json().get("rank", "N/A")
            }
        return None
    except Exception:
        return None


def format_date(dt: Optional[datetime]) -> str:
    return dt.strftime("%b %d, %Y %I:%M %p") if dt else "N/A"

def format_number(num: int) -> str:
    return f"{num:,}"


def main():
    parser = argparse.ArgumentParser(description="Citadel Cap Tracker - Lobster Edition")
    parser.add_argument("--since", type=str, default="2026-03-11", help="Check activity since YYYY-MM-DD")
    parser.add_argument("--clan", type=str, default="Lords of Arcadia", help="Clan name")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--rate-limit", type=int, default=200, help="Rate limit in ms")
    
    args = parser.parse_args()
    
    try:
        since_date = datetime.strptime(args.since, "%Y-%m-%d")
    except ValueError:
        print(f"❌ Invalid date format: {args.since}. Use YYYY-MM-DD")
        sys.exit(1)
    
    print(f"\n🏰 Citadel Cap Tracker - Lobster Edition")
    print(f"=" * 60)
    print(f"🛡️  Clan: {args.clan}")
    print(f"📅 Checking since: {since_date.strftime('%B %d, %Y')}")
    print(f"=" * 60)
    
    print(f"\n📋 Fetching clan member list...")
    members = get_clan_members(args.clan)
    
    if not members:
        print("❌ No clan members found. Check clan name.")
        sys.exit(1)
    
    print(f"👥 Found {len(members)} clan members")
    print(f"\n🔍 Checking activity logs...\n")
    
    capped_members = []
    visited_only = []
    
    for i, member in enumerate(members, 1):
        if args.verbose:
            print(f"[{i}/{len(members)}] Checking {member}...", end=" ", flush=True)
        else:
            print(f"[{i}/{len(members)}] {member}", end="\r", flush=True)
        
        result = check_player_citadel_activity(member, since_date)
        
        if result:
            if result["cap_date"]:
                capped_members.append(result)
                if args.verbose:
                    print(f"✅ CAPPED {result['cap_date'].strftime('%m/%d')}")
            elif result["visit_date"]:
                visited_only.append(result)
                if args.verbose:
                    print(f"👁️  Visited {result['visit_date'].strftime('%m/%d')}")
        else:
            if args.verbose:
                print("❌ No citadel activity")
        
        time.sleep(args.rate_limit / 1000)
    
    if not args.verbose:
        print()
    
    capped_members.sort(key=lambda x: x["cap_date"] or datetime.min, reverse=True)
    visited_only.sort(key=lambda x: x["visit_date"] or datetime.min, reverse=True)
    
    # Convert datetime to string for JSON
    for member in capped_members + visited_only:
        if member.get("cap_date"):
            member["cap_date"] = member["cap_date"].isoformat()
        if member.get("visit_date"):
            member["visit_date"] = member["visit_date"].isoformat()
    
    # JSON output
    if args.json:
        output = {
            "clan": args.clan,
            "since": args.since,
            "checked_at": datetime.now().isoformat(),
            "total_members": len(members),
            "capped": capped_members,
            "visited_only": visited_only
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)
    
    print(f"\n{'=' * 60}")
    print(f"📊 RESULTS")
    print(f"{'=' * 60}")
    
    if capped_members:
        print(f"\n✅ CAPPED CITADEL ({len(capped_members)} members since {since_date.strftime('%b %d')}):")
        print(f"{'-' * 60}")
        print(f"{'#':<4} {'Player':<25} {'Cap Date':<22} {'Visit Date':<22} {'Total XP':<15}")
        print(f"{'-' * 60}")
        
        for i, member in enumerate(capped_members, 1):
            print(f"{i:<4} {member['player']:<25} {format_date(member['cap_date']):<22} {format_date(member['visit_date']):<22} {format_number(member['total_xp']):<15}")
    else:
        print(f"\n❌ No members found who capped since {since_date.strftime('%b %d, %Y')}")
    
    if visited_only:
        print(f"\n👁️  VISITED ONLY ({len(visited_only)} members):")
        print(f"{'-' * 60}")
        for i, member in enumerate(visited_only, 1):
            print(f"{i:<4} {member['player']:<25} {format_date(member['visit_date']):<22}")
    
    print(f"\n{'=' * 60}")
    print(f"📈 SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total clan members: {len(members)}")
    print(f"Capped since {since_date.strftime('%b %d')}: {len(capped_members)} ({100*len(capped_members)/len(members):.1f}%)")
    print(f"Visited only: {len(visited_only)} ({100*len(visited_only)/len(members):.1f}%)")
    print(f"No citadel activity: {len(members) - len(capped_members) - len(visited_only)}")
    
    if args.output:
        output_data = {
            "clan": args.clan, "since": args.since, "checked_at": datetime.now().isoformat(),
            "total_members": len(members), "capped": capped_members, "visited_only": visited_only
        }
        for member in output_data["capped"] + output_data["visited_only"]:
            if member["cap_date"]: member["cap_date"] = member["cap_date"].isoformat()
            if member["visit_date"]: member["visit_date"] = member["visit_date"].isoformat()
        
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")
    
    print()


if __name__ == "__main__":
    main()
