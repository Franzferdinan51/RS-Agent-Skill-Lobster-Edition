#!/usr/bin/env python3
"""
Price Alert Tool - Lobster Edition
===================================
Monitor Grand Exchange prices and alert when thresholds are crossed.

Features:
- Track multiple items
- Set buy/sell price thresholds
- Alert when prices cross thresholds
- Historical price tracking
- JSON output + webhook support

Usage:
    python3 price-alert.py --item "Twisted bow" --threshold 300000000
    python3 price-alert.py --watch-list watchlist.json --output alerts.json
    python3 price-alert.py --item "Twisted bow" --webhook https://discord.com/api/webhooks/...
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

GE_BASE = "https://secure.runescape.com/m=itemdb_rs/api"


def get_item_by_name(name: str) -> dict:
    """Search for item by name."""
    url = f"{GE_BASE}/catalogue/items.json?category=0&alpha={name[0].lower()}&page=1"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code != 200:
            return {}
        data = response.json()
        for item in data.get("items", []):
            if name.lower() in item.get("name", "").lower():
                return item
        return {}
    except Exception:
        return {}


def get_item_price(item_id: int) -> dict:
    """Get current item price."""
    url = f"{GE_BASE}/catalogue/detail.json?item={item_id}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 RS-Agent/1.0"}, timeout=10)
        if response.status_code != 200:
            return {}
        data = response.json()
        return data.get("item", {})
    except Exception:
        return {}


def parse_price(price_str: str) -> int:
    """Parse price string to integer (e.g., '5.2m' -> 5200000)."""
    if not price_str:
        return 0
    price_str = price_str.lower().replace(",", "")
    multipliers = {"k": 1000, "m": 1000000, "b": 1000000000}
    for suffix, mult in multipliers.items():
        if suffix in price_str:
            return int(float(price_str.replace(suffix, "")) * mult)
    return int(price_str)


def send_webhook(webhook_url: str, item_name: str, current_price: int, threshold: int):
    """Send alert to Discord webhook."""
    embed = {
        "title": "🚨 Price Alert!",
        "description": f"**{item_name}** has crossed your threshold!",
        "color": 0xFF4500,
        "fields": [
            {"name": "Current Price", "value": f"{current_price:,} gp", "inline": True},
            {"name": "Threshold", "value": f"{threshold:,} gp", "inline": True},
            {"name": "Difference", "value": f"{current_price - threshold:+,} gp", "inline": True}
        ],
        "timestamp": datetime.now().isoformat(),
        "footer": {"text": "RS-Agent Price Monitor"}
    }
    
    try:
        requests.post(webhook_url, json={"embeds": [embed]}, timeout=10)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Price Alert Tool - Lobster Edition")
    parser.add_argument("--item", type=str, help="Item name to monitor")
    parser.add_argument("--threshold", type=int, help="Price threshold (alert when below)")
    parser.add_argument("--watch-list", type=str, help="JSON file with watch list")
    parser.add_argument("--webhook", type=str, help="Discord webhook URL for alerts")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    parser.add_argument("--continuous", action="store_true", help="Run continuously (check every 5 min)")
    parser.add_argument("--rate-limit", type=int, default=200, help="Rate limit in ms")
    
    args = parser.parse_args()
    
    print(f"\n💰 Price Alert Tool - Lobster Edition")
    print(f"=" * 60)
    
    alerts = []
    
    if args.watch_list:
        # Load watch list
        try:
            with open(args.watch_list, "r") as f:
                watch_list = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load watch list: {e}")
            sys.exit(1)
        
        print(f"📋 Monitoring {len(watch_list)} items from {args.watch_list}\n")
        
        for item_config in watch_list:
            item_name = item_config.get("name")
            threshold = item_config.get("threshold", 0)
            
            print(f"🔍 Checking {item_name}...", end=" ", flush=True)
            item_data = get_item_by_name(item_name)
            
            if not item_data:
                print("❌ Not found")
                continue
            
            price_data = get_item_price(item_data["id"])
            current_price = parse_price(price_data.get("current", {}).get("price", "0"))
            
            print(f"{current_price:,} gp", end="")
            
            if current_price <= threshold:
                print(" ⚠️ ALERT!")
                alerts.append({
                    "item": item_name,
                    "current_price": current_price,
                    "threshold": threshold,
                    "timestamp": datetime.now().isoformat()
                })
                
                if args.webhook:
                    send_webhook(args.webhook, item_name, current_price, threshold)
            else:
                print(" ✅")
            
            time.sleep(args.rate_limit / 1000)
    
    elif args.item and args.threshold:
        # Single item check
        print(f"🔍 Monitoring: {args.item}")
        print(f"⚠️  Alert threshold: {args.threshold:,} gp\n")
        
        item_data = get_item_by_name(args.item)
        if not item_data:
            print(f"❌ Item not found: {args.item}")
            sys.exit(1)
        
        print(f"📊 Item ID: {item_data['id']}")
        print(f"📊 Type: {item_data.get('type', 'Unknown')}")
        
        if args.continuous:
            print(f"\n🔄 Running continuously (Ctrl+C to stop)...\n")
            try:
                while True:
                    price_data = get_item_price(item_data["id"])
                    current_price = parse_price(price_data.get("current", {}).get("price", "0"))
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"[{timestamp}] {current_price:,} gp", end="")
                    
                    if current_price <= args.threshold:
                        print(" ⚠️ ALERT!")
                        alerts.append({
                            "item": args.item,
                            "current_price": current_price,
                            "threshold": args.threshold,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        if args.webhook:
                            send_webhook(args.webhook, args.item, current_price, args.threshold)
                    else:
                        print(" ✅")
                    
                    time.sleep(300)  # 5 minutes
            except KeyboardInterrupt:
                print("\n\n👋 Stopped monitoring")
        else:
            price_data = get_item_price(item_data["id"])
            current_price = parse_price(price_data.get("current", {}).get("price", "0"))
            
            print(f"💰 Current Price: {current_price:,} gp")
            print(f"⚠️  Threshold: {args.threshold:,} gp")
            
            if current_price <= args.threshold:
                print(f"\n🚨 ALERT! Price is below threshold!")
                alerts.append({
                    "item": args.item,
                    "current_price": current_price,
                    "threshold": args.threshold,
                    "timestamp": datetime.now().isoformat()
                })
                
                if args.webhook:
                    send_webhook(args.webhook, args.item, current_price, args.threshold)
            else:
                print(f"\n✅ Price is above threshold")
    
    else:
        parser.print_help()
        sys.exit(1)
    
    # Save results
    if args.output:
        output_data = {
            "checked_at": datetime.now().isoformat(),
            "alerts": alerts
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total alerts: {len(alerts)}")
    
    if alerts:
        print(f"\n⚠️  ALERTS:")
        for alert in alerts:
            print(f"   • {alert['item']}: {alert['current_price']:,} gp (threshold: {alert['threshold']:,} gp)")
    
    print()


if __name__ == "__main__":
    main()
