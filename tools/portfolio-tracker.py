#!/usr/bin/env python3
"""
Portfolio Tracker - Lobster Edition
===================================
Track your RuneScape wealth and investments.

Features:
- Add/remove items from portfolio
- Track buy prices and quantities
- Calculate current value and profit/loss
- ROI calculations with 5% GE tax
- Portfolio allocation percentages
- Wealth milestone tracking

Usage:
    python3 tools/portfolio-tracker.py --add "Twisted bow" --quantity 1 --buy-price 290000000
    python3 tools/portfolio-tracker.py --view
    python3 tools/portfolio-tracker.py --remove "Twisted bow"
    python3 tools/portfolio-tracker.py --analyze
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

PORTFOLIO_FILE = Path("data/portfolio/portfolio.json")
GE_BASE = "https://secure.runescape.com/m=itemdb_rs/api"
GE_TAX = 0.05  # 5% GE tax


def load_portfolio() -> dict:
    """Load portfolio from file."""
    if PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {"items": [], "created_at": datetime.now().isoformat(), "last_updated": None}


def save_portfolio(portfolio: dict):
    """Save portfolio to file."""
    PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    portfolio["last_updated"] = datetime.now().isoformat()
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)


def get_item_price(item_name: str) -> int:
    """Get current GE price for an item."""
    url = f"{GE_BASE}/catalogue/items.json?category=0&alpha={item_name[0].lower()}&page=1"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                if item_name.lower() in item.get("name", "").lower():
                    price_str = item.get("current", {}).get("price", "0")
                    # Parse price string (e.g., "5.2m" -> 5200000)
                    price_str = str(price_str).lower().replace(",", "")
                    if "m" in price_str:
                        return int(float(price_str.replace("m", "")) * 1000000)
                    elif "k" in price_str:
                        return int(float(price_str.replace("k", "")) * 1000)
                    elif "b" in price_str:
                        return int(float(price_str.replace("b", "")) * 1000000000)
                    return int(price_str) if price_str else 0
    except:
        pass
    return 0


def add_item(portfolio: dict, item_name: str, quantity: int, buy_price: int) -> dict:
    """Add item to portfolio."""
    # Check if item already exists
    for item in portfolio["items"]:
        if item["name"].lower() == item_name.lower():
            # Update existing item (average cost)
            total_cost = item["buy_price"] * item["quantity"] + buy_price * quantity
            item["quantity"] += quantity
            item["buy_price"] = total_cost // item["quantity"]
            item["last_added"] = datetime.now().isoformat()
            return {"status": "updated", "item": item}
    
    # Add new item
    new_item = {
        "name": item_name,
        "quantity": quantity,
        "buy_price": buy_price,
        "added_at": datetime.now().isoformat(),
        "last_added": datetime.now().isoformat()
    }
    portfolio["items"].append(new_item)
    return {"status": "added", "item": new_item}


def remove_item(portfolio: dict, item_name: str) -> dict:
    """Remove item from portfolio."""
    for i, item in enumerate(portfolio["items"]):
        if item["name"].lower() == item_name.lower():
            removed = portfolio["items"].pop(i)
            return {"status": "removed", "item": removed}
    return {"status": "not_found", "item_name": item_name}


def calculate_portfolio_value(portfolio: dict) -> dict:
    """Calculate current portfolio value and P/L."""
    total_buy_cost = 0
    total_current_value = 0
    total_tax = 0
    
    items_with_values = []
    
    for item in portfolio["items"]:
        current_price = get_item_price(item["name"])
        buy_cost = item["buy_price"] * item["quantity"]
        current_value = current_price * item["quantity"]
        sale_value = current_value * (1 - GE_TAX)  # After 5% tax
        profit_loss = sale_value - buy_cost
        roi = (profit_loss / buy_cost * 100) if buy_cost > 0 else 0
        
        total_buy_cost += buy_cost
        total_current_value += current_value
        total_tax += current_value * GE_TAX
        
        items_with_values.append({
            "name": item["name"],
            "quantity": item["quantity"],
            "buy_price": item["buy_price"],
            "current_price": current_price,
            "buy_cost": buy_cost,
            "current_value": current_value,
            "after_tax_value": sale_value,
            "profit_loss": profit_loss,
            "roi_percent": round(roi, 2),
            "allocation_percent": round((current_value / total_current_value * 100) if total_current_value > 0 else 0, 2)
        })
    
    # Recalculate allocations with final totals
    for item in items_with_values:
        item["allocation_percent"] = round((item["current_value"] / total_current_value * 100) if total_current_value > 0 else 0, 2)
    
    total_profit_loss = sum(item["profit_loss"] for item in items_with_values)
    
    return {
        "total_buy_cost": total_buy_cost,
        "total_current_value": total_current_value,
        "total_after_tax_value": total_current_value * (1 - GE_TAX),
        "total_tax": total_tax,
        "total_profit_loss": total_profit_loss,
        "total_roi_percent": round((total_profit_loss / total_buy_cost * 100) if total_buy_cost > 0 else 0, 2),
        "items": items_with_values,
        "item_count": len(items_with_values),
        "calculated_at": datetime.now().isoformat()
    }


def format_number(num: int) -> str:
    """Format number with commas."""
    return f"{num:,}"


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
    parser = argparse.ArgumentParser(description="Portfolio Tracker - Lobster Edition")
    
    action_group = parser.add_argument_group("Actions")
    action_group.add_argument("--add", type=str, help="Add item to portfolio")
    action_group.add_argument("--remove", type=str, help="Remove item from portfolio")
    action_group.add_argument("--view", action="store_true", help="View portfolio")
    action_group.add_argument("--analyze", action="store_true", help="Analyze portfolio")
    
    item_group = parser.add_argument_group("Item Details (for --add)")
    item_group.add_argument("--quantity", type=int, default=1, help="Item quantity")
    item_group.add_argument("--buy-price", type=int, help="Buy price per item")
    
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--json", action="store_true", help="JSON output")
    output_group.add_argument("--export", type=str, help="Export to file")
    
    args = parser.parse_args()
    
    portfolio = load_portfolio()
    
    # Add item
    if args.add:
        if not args.buy_price:
            print("❌ --buy-price is required when adding an item")
            sys.exit(1)
        
        result = add_item(portfolio, args.add, args.quantity, args.buy_price)
        save_portfolio(portfolio)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "✅ Updated" if result["status"] == "updated" else "✅ Added"
            print(f"\n{status} {args.add}")
            print(f"   Quantity: {result['item']['quantity']}")
            print(f"   Avg Buy Price: {format_number(result['item']['buy_price'])} gp")
        sys.exit(0)
    
    # Remove item
    if args.remove:
        result = remove_item(portfolio, args.remove)
        save_portfolio(portfolio)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result["status"] == "removed":
                print(f"\n✅ Removed {args.remove}")
            else:
                print(f"\n❌ Item not found: {args.remove}")
        sys.exit(0)
    
    # View portfolio
    if args.view or args.analyze:
        if not portfolio["items"]:
            print("\n📭 Portfolio is empty")
            print("\n💡 Add items with:")
            print("   python3 tools/portfolio-tracker.py --add \"Twisted bow\" --quantity 1 --buy-price 290000000")
            sys.exit(0)
        
        values = calculate_portfolio_value(portfolio)
        
        if args.json:
            output = {**portfolio, **values}
            print(json.dumps(output, indent=2))
            sys.exit(0)
        
        # Display portfolio
        print(f"\n💼 Portfolio - Lobster Edition")
        print(f"=" * 80)
        
        print(f"\n📊 Summary")
        print(f"{'-' * 80}")
        print(f"Items: {values['item_count']}")
        print(f"Total Buy Cost: {format_number(values['total_buy_cost'])} gp")
        print(f"Current Value: {format_number(values['total_current_value'])} gp")
        print(f"After Tax (5%): {format_number(int(values['total_after_tax_value']))} gp")
        print(f"GE Tax: {format_number(int(values['total_tax']))} gp")
        print(f"Profit/Loss: {format_number(int(values['total_profit_loss']))} gp ({values['total_roi_percent']:+.2f}%)")
        
        if values['items']:
            print(f"\n📋 Holdings")
            print(f"{'-' * 80}")
            print(f"{'Item':<30} {'Qty':<6} {'Buy':<12} {'Current':<12} {'Value':<15} {'P/L':<15} {'Alloc':<8}")
            print(f"{'-' * 80}")
            
            # Sort by value
            sorted_items = sorted(values['items'], key=lambda x: x['current_value'], reverse=True)
            
            for item in sorted_items:
                pl_str = f"{format_number(int(item['profit_loss']))} ({item['roi_percent']:+.1f}%)"
                print(f"{item['name']:<30} {item['quantity']:<6} {format_number(item['buy_price']):<12} {format_number(item['current_price']):<12} {format_number(item['current_value']):<15} {pl_str:<15} {item['allocation_percent']:.1f}%")
        
        # Milestones
        print(f"\n🎯 Wealth Milestones")
        print(f"{'-' * 80}")
        milestones = [
            (100_000_000, "100M"),
            (500_000_000, "500M"),
            (1_000_000_000, "1B"),
            (10_000_000_000, "10B"),
            (100_000_000_000, "100B"),
            (1_000_000_000_000, "1T")
        ]
        
        current_value = values['total_after_tax_value']
        for threshold, name in milestones:
            status = "✅" if current_value >= threshold else "⏳"
            print(f"{status} {name}: {format_number(threshold)} gp")
        
        print()
        
        # Export
        if args.export:
            output = {**portfolio, **values}
            with open(args.export, "w") as f:
                json.dump(output, f, indent=2)
            print(f"💾 Exported to: {args.export}")
        
        sys.exit(0)
    
    # No action specified
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
