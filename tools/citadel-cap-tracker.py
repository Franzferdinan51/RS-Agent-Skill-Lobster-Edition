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
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


if sys.platform == "win32":
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


CLAN_BASE = "https://secure.runescape.com/m=clan-hiscores"
RUNEMETRICS_BASE = "https://apps.runescape.com/runemetrics"
DATE_FORMAT = "%d-%b-%Y %H:%M"
USER_AGENT = "Mozilla/5.0 RS-Agent/1.0"


def log(message: str = "", *, enabled: bool = True, end: str = "\n", flush: bool = False) -> None:
    """Print only when human-readable output is enabled."""
    if enabled:
        print(message, end=end, flush=flush)


def build_error(message: str, **details: object) -> Dict[str, object]:
    """Build a structured error payload."""
    payload: Dict[str, object] = {"error": message}
    payload.update(details)
    return payload


def get_clan_members(clan_name: str) -> List[str]:
    """Get all clan member names."""
    url = f"{CLAN_BASE}/members_lite.ws?clanName={clan_name.replace(' ', '+')}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            return []
        lines = response.text.strip().split("\n")
        return [line.split(",")[0].replace("\u00a0", " ") for line in lines[1:] if line.split(",")]
    except Exception:
        return []


def check_player_citadel_activity(player_name: str, since_date: datetime) -> Optional[Dict[str, object]]:
    """Check if a player has capped at clan citadel since specified date."""
    url = f"{RUNEMETRICS_BASE}/profile/profile?user={player_name}&activities=100"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        profile = response.json() if response.status_code == 200 else {}
        if "activities" not in profile:
            return None

        cap_date = None
        visit_date = None
        for activity in profile["activities"]:
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

        if not cap_date and not visit_date:
            return None

        return {
            "player": player_name,
            "cap_date": cap_date,
            "visit_date": visit_date,
            "total_xp": profile.get("totalxp", 0),
            "rank": profile.get("rank", "N/A"),
        }
    except Exception:
        return None


def format_date(value: Optional[datetime]) -> str:
    return value.strftime("%b %d, %Y %I:%M %p") if value else "N/A"


def format_number(num: int) -> str:
    return f"{num:,}"


def serialize_member(member: Dict[str, object]) -> Dict[str, object]:
    """Convert datetime fields to ISO strings for JSON output."""
    serialized = dict(member)
    cap_date = serialized.get("cap_date")
    visit_date = serialized.get("visit_date")
    serialized["cap_date"] = cap_date.isoformat() if isinstance(cap_date, datetime) else None
    serialized["visit_date"] = visit_date.isoformat() if isinstance(visit_date, datetime) else None
    return serialized


def main() -> None:
    parser = argparse.ArgumentParser(description="Citadel Cap Tracker - Lobster Edition")
    parser.add_argument("--since", type=str, default="2026-03-11", help="Check activity since YYYY-MM-DD")
    parser.add_argument("--clan", type=str, default="Lords of Arcadia", help="Clan name")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--rate-limit", type=int, default=200, help="Rate limit in ms")

    args = parser.parse_args()
    json_mode = args.json
    human_mode = not json_mode
    verbose = args.verbose and human_mode

    try:
        since_date = datetime.strptime(args.since, "%Y-%m-%d")
    except ValueError:
        error = build_error("Invalid date format", since=args.since, expected="YYYY-MM-DD")
        if json_mode:
            print(json.dumps(error, indent=2))
            return
        print(f"ERROR: Invalid date format: {args.since}. Use YYYY-MM-DD")
        sys.exit(1)

    log("\n[CITADEL] Citadel Cap Tracker - Lobster Edition", enabled=human_mode)
    log("=" * 60, enabled=human_mode)
    log(f"Clan: {args.clan}", enabled=human_mode)
    log(f"Checking since: {since_date.strftime('%B %d, %Y')}", enabled=human_mode)
    log("=" * 60, enabled=human_mode)

    log("\nFetching clan member list...", enabled=human_mode)
    members = get_clan_members(args.clan)
    if not members:
        error = build_error("No clan members found. Check clan name.", clan=args.clan)
        if json_mode:
            print(json.dumps(error, indent=2))
            return
        print("ERROR: No clan members found. Check clan name.")
        sys.exit(1)

    log(f"Found {len(members)} clan members", enabled=human_mode)
    log("\nChecking activity logs...\n", enabled=human_mode)

    capped_members: List[Dict[str, object]] = []
    visited_only: List[Dict[str, object]] = []

    for index, member in enumerate(members, 1):
        if verbose:
            log(f"[{index}/{len(members)}] Checking {member}...", enabled=True, end=" ", flush=True)
        elif human_mode:
            log(f"[{index}/{len(members)}] {member}", enabled=True, end="\r", flush=True)

        result = check_player_citadel_activity(member, since_date)
        if result:
            if result["cap_date"]:
                capped_members.append(result)
                if verbose:
                    cap_date = result["cap_date"]
                    assert isinstance(cap_date, datetime)
                    log(f"CAPPED {cap_date.strftime('%m/%d')}", enabled=True)
            elif result["visit_date"]:
                visited_only.append(result)
                if verbose:
                    visit_date = result["visit_date"]
                    assert isinstance(visit_date, datetime)
                    log(f"Visited {visit_date.strftime('%m/%d')}", enabled=True)
        elif verbose:
            log("No citadel activity", enabled=True)

        time.sleep(max(args.rate_limit, 0) / 1000)

    if human_mode and not verbose:
        print()

    capped_members.sort(key=lambda item: item["cap_date"] or datetime.min, reverse=True)
    visited_only.sort(key=lambda item: item["visit_date"] or datetime.min, reverse=True)

    output_data = {
        "clan": args.clan,
        "since": args.since,
        "checked_at": datetime.now().isoformat(),
        "total_members": len(members),
        "capped": [serialize_member(member) for member in capped_members],
        "visited_only": [serialize_member(member) for member in visited_only],
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(output_data, file, indent=2)
        log(f"\nResults saved to: {args.output}", enabled=human_mode)

    if json_mode:
        print(json.dumps(output_data, indent=2))
        return

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    if capped_members:
        print(f"\nCAPPED CITADEL ({len(capped_members)} members since {since_date.strftime('%b %d')}):")
        print("-" * 60)
        print(f"{'#':<4} {'Player':<25} {'Cap Date':<22} {'Visit Date':<22} {'Total XP':<15}")
        print("-" * 60)
        for index, member in enumerate(capped_members, 1):
            print(
                f"{index:<4} {member['player']:<25} {format_date(member['cap_date']):<22} "
                f"{format_date(member['visit_date']):<22} {format_number(int(member['total_xp'])):<15}"
            )
    else:
        print(f"\nNo members found who capped since {since_date.strftime('%b %d, %Y')}")

    if visited_only:
        print(f"\nVISITED ONLY ({len(visited_only)} members):")
        print("-" * 60)
        for index, member in enumerate(visited_only, 1):
            print(f"{index:<4} {member['player']:<25} {format_date(member['visit_date']):<22}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total clan members: {len(members)}")
    print(f"Capped since {since_date.strftime('%b %d')}: {len(capped_members)} ({100 * len(capped_members) / len(members):.1f}%)")
    print(f"Visited only: {len(visited_only)} ({100 * len(visited_only) / len(members):.1f}%)")
    print(f"No citadel activity: {len(members) - len(capped_members) - len(visited_only)}")
    print()


if __name__ == "__main__":
    main()
