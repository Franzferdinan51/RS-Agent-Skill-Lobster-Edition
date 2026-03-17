#!/usr/bin/env python3
"""
Advanced GE Trading Strategies - Lobster Edition
================================================
Advanced flipping and merchanting strategies.

Usage:
    python3 tools/advanced-trading.py --strategy bulk-flip --item "Twisted bow"
    python3 tools/advanced-trading.py --strategy merchant --target-profit 1000000
    python3 tools/advanced-trading.py --strategy trend --item "Dragon scimitar"
"""

import argparse
import json
import sys

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

GE_BASE = "https://secure.runescape.com/m=itemdb_rs/api"
GE_TAX = 0.05


def get_item_price(item_name: str) -> dict:
    """Get current item price and limits."""
    url = f"{GE_BASE}/catalogue/detail.json?item={item_name}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code == 200:
            return response.json().get("item", {})
    except:
        pass
    return {}


def calculate_bulk_flip(buy_price: int, sell_price: int, quantity: int) -> dict:
    """Calculate bulk flip profits with tax optimization."""
    total_buy = buy_price * quantity
    total_sell = sell_price * quantity
    tax = int(total_sell * GE_TAX)
    profit = total_sell - total_buy - tax
    roi = (profit / total_buy * 100) if total_buy > 0 else 0
    
    # Optimal quantity for maximum profit within buy limits
    buy_limit = 10000  # Typical GE limit
    optimal_qty = min(quantity, buy_limit)
    
    return {
        "buy_price": buy_price,
        "sell_price": sell_price,
        "quantity": quantity,
        "total_buy": total_buy,
        "total_sell": total_sell,
        "ge_tax": tax,
        "profit": profit,
        "roi_percent": round(roi, 2),
        "optimal_quantity": optimal_qty,
        "profit_per_hour_estimate": profit * 2  # Assumes 2 flips/day
    }


def merchant_calculator(target_profit: int, margin_percent: float) -> dict:
    """Calculate merchanting requirements."""
    # Work backwards from target profit
    # Profit = (Sell * 0.95) - Buy
    # Target: Profit = target_profit
    
    min_volume = int(target_profit / (margin_percent / 100)) if margin_percent > 0 else 0
    
    return {
        "target_profit": target_profit,
        "margin_percent": margin_percent,
        "minimum_volume": min_volume,
        "estimated_capital_required": min_volume * 10000,  # Avg item price estimate
        "trips_required": max(1, min_volume // 500),  # Assuming 500 items per trip
        "time_estimate_hours": max(1, min_volume // 500 * 0.5)  # 30 min per trip
    }


def trend_analysis(item_name: str) -> dict:
    """Analyze price trends for an item."""
    item = get_item_price(item_name)
    if not item:
        return {"error": "Item not found"}
    
    current = item.get("current", {})
    today = item.get("today", {})
    day90 = item.get("day90", {})
    
    # Calculate trend strength
    trend_score = 0
    if current.get("trend") == "positive":
        trend_score += 1
    if today.get("trend") == "positive":
        trend_score += 1
    if day90.get("trend") == "positive":
        trend_score += 1
    
    # Signal generation
    signal = "HOLD"
    if trend_score >= 3:
        signal = "STRONG_BUY"
    elif trend_score == 2:
        signal = "BUY"
    elif trend_score == 0:
        signal = "STRONG_SELL"
    elif trend_score == 1:
        signal = "SELL"
    
    return {
        "item": item.get("name", item_name),
        "current_price": current.get("price", "N/A"),
        "current_trend": current.get("trend", "neutral"),
        "today_change": today.get("price", 0),
        "today_trend": today.get("trend", "neutral"),
        "day90_change": day90.get("change", "0%"),
        "day90_trend": day90.get("trend", "neutral"),
        "trend_score": trend_score,
        "signal": signal,
        "recommendation": f"Based on trend analysis: {signal}"
    }


def main():
    parser = argparse.ArgumentParser(description="Advanced Trading Strategies - Lobster Edition")
    parser.add_argument("--strategy", type=str, required=True,
                       choices=["bulk-flip", "merchant", "trend"],
                       help="Trading strategy")
    parser.add_argument("--item", type=str, help="Item name")
    parser.add_argument("--buy-price", type=int, help="Buy price per item")
    parser.add_argument("--sell-price", type=int, help="Sell price per item")
    parser.add_argument("--quantity", type=int, default=100, help="Quantity to flip")
    parser.add_argument("--target-profit", type=int, help="Target profit (for merchant)")
    parser.add_argument("--margin", type=float, default=5.0, help="Target margin %")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    result = {}
    
    if args.strategy == "bulk-flip":
        if not args.item or not args.buy_price or not args.sell_price:
            print("❌ --item, --buy-price, and --sell-price required for bulk-flip")
            sys.exit(1)
        result = calculate_bulk_flip(args.buy_price, args.sell_price, args.quantity)
        result["strategy"] = "bulk_flip"
        result["item"] = args.item
    
    elif args.strategy == "merchant":
        target = args.target_profit or 1000000
        result = merchant_calculator(target, args.margin)
        result["strategy"] = "merchant"
    
    elif args.strategy == "trend":
        if not args.item:
            print("❌ --item required for trend analysis")
            sys.exit(1)
        result = trend_analysis(args.item)
        result["strategy"] = "trend"
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n💼 Advanced Trading Strategy: {args.strategy.replace('-', ' ').title()}")
        print(f"{'=' * 60}")
        
        for key, value in result.items():
            if isinstance(value, (int, float)):
                print(f"{key.replace('_', ' ').title()}: {value:,}" if value > 1000 else f"{key.replace('_', ' ').title()}: {value}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print()


if __name__ == "__main__":
    main()
