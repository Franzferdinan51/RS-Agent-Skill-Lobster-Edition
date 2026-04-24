#!/usr/bin/env python3
"""
Inactive Member Tracker - Lobster Edition
==========================================
Find clan members who have not been active for a configurable number of days.
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
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
    if enabled:
        print(message, end=end, flush=flush)


def build_error(message: str, **details: object) -> Dict[str, object]:
    payload: Dict[str, object] = {"error": message}
    payload.update(details)
    return payload


def get_clan_members(clan_name: str) -> List[Dict[str, object]]:
    """Get all clan member names with XP data."""
    url = f"{CLAN_BASE}/members_lite.ws?clanName={clan_name.replace(' ', '+')}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            return []
        lines = response.text.strip().split("\n")
        if not lines or not lines[0].lower().startswith("clanmate"):
            return []
        members: List[Dict[str, object]] = []
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) < 3:
                continue
            members.append({
                "name": parts[0].replace("\u00a0", " "),
                "rank": parts[1],
                "total_xp": int(parts[2]) if parts[2].isdigit() else 0,
            })
        return members
    except Exception:
        return []


def check_player_activity(player_name: str) -> Dict[str, object]:
    """Check player's last activity date from Runemetrics."""
    url = f"{RUNEMETRICS_BASE}/profile/profile?user={player_name}&activities=5"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            return {"player": player_name, "error": "Profile private or not found"}

        data = response.json()
        result: Dict[str, object] = {
            "player": player_name,
            "total_xp": data.get("totalxp", 0),
            "combat_level": data.get("combatlevel", 0),
            "logged_in": data.get("loggedIn", "false") == "true",
        }

        activities = data.get("activities") or []
        if activities:
            try:
                last_activity = activities[0]
                activity_date = datetime.strptime(last_activity["date"], DATE_FORMAT)
                result["last_activity"] = activity_date
                result["last_activity_type"] = last_activity.get("text", "Unknown")
                result["days_inactive"] = (datetime.now() - activity_date).days
            except (ValueError, KeyError):
                pass

        if "last_activity" not in result:
            result["error"] = "No activity data available"

        return result
    except Exception as exc:
        return {"player": player_name, "error": str(exc)}


def format_date(value: Optional[datetime]) -> str:
    return value.strftime("%b %d, %Y") if value else "N/A"


def format_xp(xp: int) -> str:
    if xp >= 1_000_000_000:
        return f"{xp / 1_000_000_000:.2f}B"
    if xp >= 1_000_000:
        return f"{xp / 1_000_000:.2f}M"
    if xp >= 1_000:
        return f"{xp / 1_000:.1f}K"
    return str(xp)


def serialize_member(member: Dict[str, object]) -> Dict[str, object]:
    serialized = dict(member)
    last_activity = serialized.get("last_activity")
    if isinstance(last_activity, datetime):
        serialized["last_activity"] = last_activity.isoformat()
    return serialized


def scan_member(member: Dict[str, object]) -> Dict[str, object]:
    activity = check_player_activity(str(member["name"]))
    activity["clan_rank"] = member["rank"]
    activity["clan_xp"] = member["total_xp"]
    return activity


def main() -> None:
    parser = argparse.ArgumentParser(description="Inactive Member Tracker - Lobster Edition")
    parser.add_argument("--days", type=int, default=90, help="Days of inactivity to flag")
    parser.add_argument("--clan", type=str, default="Lords of Arcadia", help="Clan name")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--all", action="store_true", help="Show all members")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent Runemetrics requests")
    parser.add_argument("--rate-limit", type=int, default=150, help="Deprecated; retained for compatibility")

    args = parser.parse_args()
    human_mode = not args.json
    verbose = args.verbose and human_mode
    cutoff_date = datetime.now() - timedelta(days=args.days)

    log("\nInactive Member Tracker - Lobster Edition", enabled=human_mode)
    log("=" * 70, enabled=human_mode)
    log(f"Clan: {args.clan}", enabled=human_mode)
    log(f"Checking for inactivity: {args.days}+ days (since {cutoff_date.strftime('%b %d, %Y')})", enabled=human_mode)
    log("=" * 70, enabled=human_mode)

    log("\nFetching clan member list...", enabled=human_mode)
    members = get_clan_members(args.clan)
    if not members:
        error = build_error("No clan members found", clan=args.clan)
        if args.json:
            print(json.dumps(error, indent=2))
            return
        print("ERROR: No clan members found.")
        sys.exit(1)

    log(f"Found {len(members)} clan members", enabled=human_mode)
    log("Checking activity logs...\n", enabled=human_mode)

    inactive_members: List[Dict[str, object]] = []
    active_members: List[Dict[str, object]] = []
    error_members: List[Dict[str, object]] = []
    all_members: List[Dict[str, object]] = []

    max_workers = max(1, min(args.workers, len(members)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(scan_member, member): member for member in members}
        for index, future in enumerate(as_completed(future_map), 1):
            activity = future.result()
            all_members.append(activity)

            if activity.get("error"):
                error_members.append(activity)
            elif activity.get("days_inactive") is not None and int(activity["days_inactive"]) >= args.days:
                inactive_members.append(activity)
            else:
                active_members.append(activity)

            if verbose:
                status = "INACTIVE" if activity in inactive_members else "OK"
                log(f"[{index}/{len(members)}] {activity.get('player', 'Unknown')}: {status}", enabled=True)
            elif human_mode:
                log(f"[{index}/{len(members)}] {activity.get('player', 'Unknown')}", enabled=True, end="\r", flush=True)

    if human_mode and not verbose:
        print()

    inactive_members.sort(key=lambda item: int(item.get("days_inactive") or 0), reverse=True)
    output = {
        "clan": args.clan,
        "checked_at": datetime.now().isoformat(),
        "inactivity_threshold_days": args.days,
        "total_members": len(members),
        "inactive_members": [serialize_member(member) for member in inactive_members],
        "active_count": len(active_members),
        "inactive_count": len(inactive_members),
        "error_count": len(error_members),
    }
    if args.all:
        output["all_members"] = [serialize_member(member) for member in all_members]

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=2)
        log(f"\nResults saved to: {args.output}", enabled=human_mode)

    if args.json:
        print(json.dumps(output, indent=2))
        return

    print(f"\n{'=' * 70}\nRESULTS\n{'=' * 70}")
    if inactive_members:
        print(f"\nINACTIVE MEMBERS ({len(inactive_members)} members - {args.days}+ days)")
        print(f"{'-' * 70}")
        print(f"{'#':<4} {'Player':<25} {'Days':<10} {'Last Active':<15} {'Rank':<18} {'XP':<12}")
        print(f"{'-' * 70}")
        for index, member in enumerate(inactive_members, 1):
            last_activity = member.get("last_activity")
            print(
                f"{index:<4} {member['player']:<25} {member.get('days_inactive', 'N/A'):<10} "
                f"{format_date(last_activity if isinstance(last_activity, datetime) else None):<15} "
                f"{str(member['clan_rank'])[:17]:<18} {format_xp(int(member['clan_xp'])):<12}"
            )
    else:
        print(f"\nNo members inactive for {args.days}+ days.")

    print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
    print(f"Total clan members: {len(members)}")
    print(f"Active (< {args.days} days): {len(active_members)} ({100 * len(active_members) / len(members):.1f}%)")
    print(f"Inactive ({args.days}+ days): {len(inactive_members)} ({100 * len(inactive_members) / len(members):.1f}%)")
    print(f"Errors/Unknown: {len(error_members)} ({100 * len(error_members) / len(members):.1f}%)")
    print()


if __name__ == "__main__":
    main()
