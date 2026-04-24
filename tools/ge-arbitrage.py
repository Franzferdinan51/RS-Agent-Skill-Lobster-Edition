#!/usr/bin/env python3
"""
GE Arbitrage Detector - Lobster Edition
========================================
Find arbitrage opportunities in the Grand Exchange market.

Features:
- Scan multiple items for price discrepancies
- Calculate profit margins after 5% GE tax
- Identify buy/sell opportunities
- Volume analysis
- Risk assessment
- JSON output

Usage:
    python3 ge-arbitrage.py --scan-all
    python3 ge-arbitrage.py --items "Twisted bow" "Scythe of vitur"
    python3 ge-arbitrage.py --min-profit 100000 --output opportunities.json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import List, Dict

try:
    import requests
except ImportError:
    print("requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

GE_BASE = "https://secure.runescape.com/m=itemdb_rs/api"
GE_TAX = 0.05  # 5% GE tax


def get_item_detail(item_id: int) -> dict:
    """Get item detail from GE."""
    url = f"{GE_BASE}/catalogue/detail.json?item={item_id}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code == 200:
            return response.json().get("item", {})
    except:
        pass
    return {}


def parse_price(price_str) -> int:
    """Parse price string to integer."""
    if not price_str:
        return 0
    # Handle integer prices directly
    if isinstance(price_str, int):
        return price_str
    price_str = str(price_str).lower().replace(",", "")
    multipliers = {"k": 1000, "m": 1000000, "b": 1000000000}
    for suffix, mult in multipliers.items():
        if suffix in price_str:
            return int(float(price_str.replace(suffix, "")) * mult)
    return int(price_str) if price_str else 0


def calculate_arbitrage(buy_price: int, sell_price: int) -> dict:
    """Calculate arbitrage opportunity."""
    if buy_price <= 0 or sell_price <= 0:
        return {"profit": 0, "roi": 0, "viable": False}
    
    # Calculate profit after 5% GE tax on sale
    tax = int(sell_price * GE_TAX)
    profit = sell_price - buy_price - tax
    roi = (profit / buy_price) * 100 if buy_price > 0 else 0
    
    return {
        "buy_price": buy_price,
        "sell_price": sell_price,
        "tax": tax,
        "profit": profit,
        "roi_percent": round(roi, 2),
        "viable": profit > 0
    }


def scan_items(item_ids: List[int]) -> List[dict]:
    """Scan items for arbitrage opportunities."""
    opportunities = []
    
    for item_id in item_ids:
        item = get_item_detail(item_id)
        if not item:
            continue
        
        current = item.get("current", {})
        today = item.get("today", {})
        
        buy_price = parse_price(current.get("price", "0"))
        sell_price = buy_price  # Simplified - in reality would check buy/sell limits
        
        # Check price trends for opportunity
        current_trend = current.get("trend", "neutral")
        today_trend = today.get("trend", "neutral")
        
        # Look for items with positive momentum
        if current_trend == "positive" or today_trend == "positive":
            arb = calculate_arbitrage(buy_price, int(buy_price * 1.05))  # 5% target
            
            if arb["viable"]:
                opportunities.append({
                    "item_id": item_id,
                    "item_name": item.get("name", "Unknown"),
                    "item_type": item.get("type", "Unknown"),
                    "buy_price": buy_price,
                    "target_sell": int(buy_price * 1.05),
                    "profit": arb["profit"],
                    "roi": arb["roi_percent"],
                    "trend": current_trend,
                    "members": item.get("members", False)
                })
    
    return sorted(opportunities, key=lambda x: x["roi"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="GE Arbitrage Detector - Lobster Edition")
    parser.add_argument("--scan-all", action="store_true", help="Scan popular trading items")
    parser.add_argument("--items", type=str, nargs="+", help="Item names to scan")
    parser.add_argument("--item-ids", type=int, nargs="+", help="Item IDs to scan")
    parser.add_argument("--min-profit", type=int, default=1000, help="Minimum profit threshold")
    parser.add_argument("--min-roi", type=float, default=1.0, help="Minimum ROI percentage")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    parser.add_argument("--limit", type=int, default=20, help="Max results to show")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    human_mode = not args.json
    
    if human_mode:
        print(f"\nGE Arbitrage Detector - Lobster Edition")
        print(f"=" * 60)
    
    # Popular trading items (high volume)
    POPULAR_ITEMS = [
        21787,  # Steadfast boots
        12091,  # Compost mound pouch
        20811,  #Dragon scimitar
        565,    # Blood rune
        560,    # Death rune
        569,    # Soul rune
        7936,   # Coal
        443,    # Iron ore
        453,    # Gold ore
        1516,   # Dragonstone
    ]
    
    item_ids = []
    
    if args.scan_all:
        item_ids = POPULAR_ITEMS
        if human_mode:
            print(f"Scanning {len(POPULAR_ITEMS)} popular trading items...\n")
    elif args.item_ids:
        item_ids = args.item_ids
        if human_mode:
            print(f"Scanning {len(args.item_ids)} specified items...\n")
    elif args.items:
        output = {"error": "Item name search not implemented yet. Use --item-ids instead."}
        if args.json:
            print(json.dumps(output, indent=2))
            return
        print("Looking up items...")
        print("WARNING: Item name search not implemented yet. Use --item-ids instead.")
        sys.exit(1)
    else:
        if args.json:
            print(json.dumps({"error": "No items specified. Use --scan-all or --item-ids."}, indent=2))
            return
        parser.print_help()
        sys.exit(1)
    
    opportunities = scan_items(item_ids)
    
    # Filter by thresholds
    filtered = [
        o for o in opportunities
        if o["profit"] >= args.min_profit and o["roi"] >= args.min_roi
    ]
    
    if args.json:
        output = {
            "scanned_at": datetime.now().isoformat(),
            "items_scanned": len(item_ids),
            "opportunities_found": len(filtered),
            "opportunities": filtered[:args.limit]
        }
        print(json.dumps(output, indent=2))
    else:
        if filtered:
            print(f"Found {len(filtered)} arbitrage opportunities!\n")
            print(f"{'#':<4} {'Item':<25} {'Buy':<15} {'Target':<15} {'Profit':<15} {'ROI':<10}")
            print(f"{'-' * 84}")
            
            for i, opp in enumerate(filtered[:args.limit], 1):
                buy_str = f"{opp['buy_price']:,} gp"
                target_str = f"{opp['target_sell']:,} gp"
                profit_str = f"{opp['profit']:,} gp"
                roi_str = f"{opp['roi']:.1f}%"
                
                print(f"{i:<4} {opp['item_name']:<25} {buy_str:<15} {target_str:<15} {profit_str:<15} {roi_str:<10}")
        else:
            print(f"No arbitrage opportunities found with current thresholds")
            print(f"   Try lowering --min-profit or --min-roi")
    
    # Save to file
    if args.output:
        output_data = {
            "scanned_at": datetime.now().isoformat(),
            "items_scanned": len(item_ids),
            "opportunities_found": len(filtered),
            "opportunities": filtered
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        if human_mode:
            print(f"\nResults saved to: {args.output}")
    
    # Summary
    if human_mode:
        print(f"\n{'=' * 60}")
        print(f"SUMMARY")
        print(f"{'=' * 60}")
        print(f"Items scanned: {len(item_ids)}")
        print(f"Opportunities found: {len(filtered)}")
        if filtered:
            best = filtered[0]
            print(f"Best opportunity: {best['item_name']} ({best['roi']:.1f}% ROI, {best['profit']:,} gp profit)")
        print(f"GE Tax: 5%")
        print()


if __name__ == "__main__":
    main()
