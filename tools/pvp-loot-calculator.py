#!/usr/bin/env python3
"""
PvP Loot Calculator - Lobster Edition
=====================================
Calculate PvP loot values and profit/loss.

Usage:
    python3 tools/pvp-loot-calculator.py --kill --loot "Twisted bow" "Arcane sigil"
    python3 tools/pvp-loot-calculator.py --session --value 50000000 --risk 10000000
"""

import argparse
import json
import sys
from datetime import datetime

GE_BASE = "https://secure.runescape.com/m=itemdb_rs/api"


def get_item_value(item_name: str) -> int:
    """Get current GE value of an item."""
    url = f"{GE_BASE}/catalogue/detail.json?item={item_name}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code == 200:
            data = response.json().get("item", {})
            price_str = data.get("current", {}).get("price", "0")
            # Parse price string
            price_str = str(price_str).lower().replace(",", "")
            if "m" in price_str:
                return int(float(price_str.replace("m", "")) * 1000000)
            elif "k" in price_str:
                return int(float(price_str.replace("k", "")) * 1000)
            return int(price_str) if price_str else 0
    except:
        pass
    return 0


def calculate_kill_profit(loot_items: list, risk_value: int = 0) -> dict:
    """Calculate profit from a PvP kill."""
    total_loot = 0
    loot_details = []
    
    for item in loot_items:
        value = get_item_value(item)
        total_loot += value
        loot_details.append({"item": item, "value": value})
    
    profit = total_loot - risk_value
    roi = (profit / risk_value * 100) if risk_value > 0 else 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "loot": loot_details,
        "total_loot_value": total_loot,
        "risk_value": risk_value,
        "profit": profit,
        "roi_percent": round(roi, 2),
        "profitable": profit > 0
    }


def track_session(session_data: list) -> dict:
    """Track a PvP session with multiple kills."""
    total_kills = len(session_data)
    total_profit = sum(k.get("profit", 0) for k in session_data)
    profitable_kills = sum(1 for k in session_data if k.get("profit", 0) > 0)
    win_rate = (profitable_kills / total_kills * 100) if total_kills > 0 else 0
    
    best_kill = max(session_data, key=lambda x: x.get("profit", 0)) if session_data else {}
    worst_kill = min(session_data, key=lambda x: x.get("profit", 0)) if session_data else {}
    
    return {
        "session_summary": {
            "total_kills": total_kills,
            "profitable_kills": profitable_kills,
            "losses": total_kills - profitable_kills,
            "win_rate_percent": round(win_rate, 2),
            "total_profit": total_profit,
            "profit_per_kill": total_profit // total_kills if total_kills > 0 else 0
        },
        "best_kill": best_kill,
        "worst_kill": worst_kill
    }


def main():
    parser = argparse.ArgumentParser(description="PvP Loot Calculator - Lobster Edition")
    parser.add_argument("--kill", action="store_true", help="Calculate single kill profit")
    parser.add_argument("--loot", type=str, nargs="+", help="Loot items received")
    parser.add_argument("--risk", type=int, default=0, help="Risk value (gear lost on death)")
    parser.add_argument("--session", action="store_true", help="Track full session")
    parser.add_argument("--value", type=int, help="Total loot value (for session)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    result = {}
    
    if args.kill and args.loot:
        result = calculate_kill_profit(args.loot, args.risk)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n⚔️  PvP Kill Profit Calculator")
            print(f"{'=' * 60}")
            print(f"📦 Loot Received:")
            for item in result["loot"]:
                print(f"   • {item['item']}: {item['value']:,} gp")
            print(f"\n💰 Total Loot: {result['total_loot_value']:,} gp")
            print(f"⚠️  Risk Value: {result['risk_value']:,} gp")
            print(f"{'=' * 60}")
            profit_str = f"+{result['profit']:,}" if result['profit'] > 0 else f"{result['profit']:,}"
            print(f"🎯 Profit: {profit_str} gp ({result['roi_percent']:+.2f}%)")
            print(f"✅ Profitable: {'Yes' if result['profitable'] else 'No'}")
            print()
    
    elif args.session and args.value:
        # Single session summary
        session = [{"profit": args.value - args.risk}]
        result = track_session(session)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n📊 PvP Session Summary")
            print(f"{'=' * 60}")
            summary = result["session_summary"]
            print(f"Total Kills: {summary['total_kills']}")
            print(f"Profitable: {summary['profitable_kills']} ({summary['win_rate_percent']:.1f}%)")
            print(f"Total Profit: {summary['total_profit']:,} gp")
            print(f"Profit/Kill: {summary['profit_per_kill']:,} gp")
            print()
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
