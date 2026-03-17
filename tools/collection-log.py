#!/usr/bin/env python3
"""
Collection Log Tracker - Lobster Edition
========================================
Track collection log progress offline.

Usage:
    python3 tools/collection-log.py --add "Twisted bow" --category "Raids"
    python3 tools/collection-log.py --view
    python3 tools/collection-log.py --progress
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

COLLECTION_FILE = Path("data/collection-log.json")


def load_collection() -> dict:
    """Load collection data."""
    if COLLECTION_FILE.exists():
        with open(COLLECTION_FILE, "r") as f:
            return json.load(f)
    return {"entries": [], "categories": {}, "started_at": datetime.now().isoformat()}


def save_collection(data: dict):
    """Save collection data."""
    COLLECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(COLLECTION_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_entry(collection: dict, item: str, category: str, source: str = "") -> dict:
    """Add item to collection."""
    entry = {
        "item": item,
        "category": category,
        "source": source,
        "obtained_at": datetime.now().isoformat()
    }
    collection["entries"].append(entry)
    
    if category not in collection["categories"]:
        collection["categories"][category] = []
    collection["categories"][category].append(item)
    
    return entry


def calculate_progress(collection: dict) -> dict:
    """Calculate collection progress."""
    total_entries = len(collection["entries"])
    categories = len(collection["categories"])
    
    # Category breakdown
    category_progress = {}
    for cat, items in collection["categories"].items():
        category_progress[cat] = {
            "count": len(items),
            "items": items
        }
    
    return {
        "total_entries": total_entries,
        "total_categories": categories,
        "category_breakdown": category_progress,
        "started_at": collection.get("started_at", "Unknown"),
        "last_updated": collection.get("last_updated", "Never")
    }


def main():
    parser = argparse.ArgumentParser(description="Collection Log Tracker - Lobster Edition")
    parser.add_argument("--add", type=str, help="Add item to collection")
    parser.add_argument("--category", type=str, help="Item category")
    parser.add_argument("--source", type=str, default="", help="Item source (boss, activity, etc.)")
    parser.add_argument("--view", action="store_true", help="View collection")
    parser.add_argument("--progress", action="store_true", help="Show progress")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    collection = load_collection()
    
    if args.add:
        if not args.category:
            print("❌ --category required when adding item")
            sys.exit(1)
        
        entry = add_entry(collection, args.add, args.category, args.source)
        save_collection(collection)
        
        if args.json:
            print(json.dumps({"status": "added", "entry": entry}, indent=2))
        else:
            print(f"\n✅ Added to Collection Log:")
            print(f"   Item: {entry['item']}")
            print(f"   Category: {entry['category']}")
            if entry['source']:
                print(f"   Source: {entry['source']}")
            print(f"   Obtained: {entry['obtained_at'][:10]}")
            print()
        sys.exit(0)
    
    if args.view:
        if not collection["entries"]:
            print("\n📭 Collection log is empty")
            print("\n💡 Add items with:")
            print("   python3 tools/collection-log.py --add \"Twisted bow\" --category \"Raids\"")
            sys.exit(0)
        
        if args.json:
            print(json.dumps(collection, indent=2))
        else:
            print(f"\n📖 Collection Log")
            print(f"{'=' * 60}")
            print(f"Total Items: {len(collection['entries'])}")
            print(f"Categories: {len(collection['categories'])}")
            print(f"\n📋 Entries:")
            for entry in collection["entries"][-20:]:  # Last 20 items
                print(f"   • {entry['item']} ({entry['category']})")
            print()
        sys.exit(0)
    
    if args.progress:
        progress = calculate_progress(collection)
        
        if args.json:
            print(json.dumps(progress, indent=2))
        else:
            print(f"\n📊 Collection Progress")
            print(f"{'=' * 60}")
            print(f"Total Items: {progress['total_entries']}")
            print(f"Categories: {progress['total_categories']}")
            print(f"\n📋 Category Breakdown:")
            for cat, data in progress['category_breakdown'].items():
                print(f"   {cat}: {data['count']} items")
            print()
        sys.exit(0)
    
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
