#!/usr/bin/env python3
"""
RS-Agent MCP Server - Lobster Edition (v2.0.8)
============================================================
Properly implements MCP protocol with correct argument handling.

Fixes:
- Empty responses (tools not executing)
- Argument type errors (booleans, integers)
- Proper CLI argument mapping
- Error handling and debugging

Usage:
    python3 mcp-server.py
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import traceback

# Tools directory
TOOLS_DIR = Path(__file__).parent / "tools"


class RS_Agent_MCP_Server:
    """MCP Server implementation for RuneScape tools."""
    
    PROTOCOL_VERSION = "2024-11-05"
    SERVER_NAME = "rs-agent-mcp"
    SERVER_VERSION = "2.0.8"
    
    def __init__(self):
        self.tools = self._register_tools()
        self.initialized = False
    
    def _register_tools(self) -> List[Dict]:
        """Register all available tools."""
        return [
            {
                "name": "runescape_api",
                "description": "Full RuneScape API client (GE, Hiscores, Clans, Runemetrics). Supports both RS3 and OSRS.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "clan": {"type": "string", "description": "Clan name to lookup"},
                        "player": {"type": "string", "description": "Player name to lookup"},
                        "item": {"type": "string", "description": "Item name to search"},
                        "item_id": {"type": "integer", "description": "Item ID for detail lookup"},
                        "game": {"type": "string", "enum": ["rs3", "osrs"], "default": "rs3", "description": "Game version"}
                    }
                }
            },
            {
                "name": "osrs_hiscores",
                "description": "Lookup Old School RuneScape or RS3 player hiscores and activity data.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "player": {"type": "string", "description": "Player name", "required": True},
                        "game": {"type": "string", "enum": ["rs3", "osrs"], "default": "rs3", "description": "Game version"},
                        "skills_only": {"type": "boolean", "default": False, "description": "Show only skills"},
                        "activities_only": {"type": "boolean", "default": False, "description": "Show only activities"}
                    }
                }
            },
            {
                "name": "citadel_tracker",
                "description": "Track clan citadel capping activity since a specified date.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "clan": {"type": "string", "description": "Clan name", "required": True},
                        "since": {"type": "string", "description": "Date (YYYY-MM-DD)", "default": "2026-03-11"}
                    }
                }
            },
            {
                "name": "inactive_members",
                "description": "Find clan members inactive for X+ days.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "clan": {"type": "string", "description": "Clan name", "required": True},
                        "days": {"type": "integer", "default": 90, "description": "Days of inactivity"}
                    }
                }
            },
            {
                "name": "player_lookup",
                "description": "Comprehensive player profile lookup for RS3 or OSRS.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "player": {"type": "string", "description": "Player name", "required": True},
                        "game": {"type": "string", "enum": ["rs3", "osrs"], "default": "rs3", "description": "Game version"},
                        "full": {"type": "boolean", "default": False, "description": "Include full profile with activity"}
                    }
                }
            },
            {
                "name": "price_alert",
                "description": "Monitor GE prices and alert when thresholds are crossed.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "item": {"type": "string", "description": "Item name", "required": True},
                        "threshold": {"type": "integer", "description": "Price threshold", "required": True},
                        "continuous": {"type": "boolean", "default": False, "description": "Run continuously"}
                    }
                }
            },
            {
                "name": "ge_arbitrage",
                "description": "Find arbitrage opportunities in the Grand Exchange market.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scan_all": {"type": "boolean", "default": True, "description": "Scan popular items"},
                        "min_profit": {"type": "integer", "default": 10000, "description": "Minimum profit"},
                        "min_roi": {"type": "number", "default": 1.0, "description": "Minimum ROI %"}
                    }
                }
            },
            {
                "name": "portfolio_tracker",
                "description": "Track RuneScape wealth and investments with P/L calculations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["view", "add", "remove", "analyze"], "required": True, "description": "Action to perform"},
                        "item": {"type": "string", "description": "Item name (for add/remove)"},
                        "quantity": {"type": "integer", "default": 1, "description": "Quantity (for add)"},
                        "buy_price": {"type": "integer", "description": "Buy price per item (for add)"}
                    }
                }
            },
            {
                "name": "auto_report",
                "description": "Generate automated reports (daily, weekly, clan, portfolio).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["daily", "weekly", "monthly", "clan", "portfolio"], "required": True, "description": "Report type"},
                        "clan": {"type": "string", "description": "Clan name (for clan reports)"},
                        "format": {"type": "string", "enum": ["html", "json", "markdown"], "default": "html", "description": "Output format"}
                    }
                }
            },
            {
                "name": "advanced_trading",
                "description": "Advanced GE trading strategies (bulk flip, merchant, trend).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "strategy": {"type": "string", "enum": ["bulk-flip", "merchant", "trend"], "required": True, "description": "Trading strategy"},
                        "item": {"type": "string", "description": "Item name"},
                        "buy_price": {"type": "integer", "description": "Buy price per item"},
                        "sell_price": {"type": "integer", "description": "Sell price per item"},
                        "quantity": {"type": "integer", "default": 100, "description": "Quantity to flip"},
                        "target_profit": {"type": "integer", "description": "Target profit (for merchant)"},
                        "margin": {"type": "number", "default": 5.0, "description": "Target margin %"}
                    }
                }
            },
            {
                "name": "pvp_loot",
                "description": "Calculate PvP loot values and profit/loss.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "kill": {"type": "boolean", "description": "Calculate single kill profit"},
                        "loot": {"type": "array", "items": {"type": "string"}, "description": "Loot items received"},
                        "risk": {"type": "integer", "default": 0, "description": "Risk value (gear lost on death)"},
                        "session": {"type": "boolean", "description": "Track full session"},
                        "value": {"type": "integer", "description": "Total loot value (for session)"}
                    }
                }
            },
            {
                "name": "collection_log",
                "description": "Track collection log progress offline.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "add": {"type": "string", "description": "Add item to collection"},
                        "category": {"type": "string", "description": "Item category"},
                        "source": {"type": "string", "default": "", "description": "Item source"},
                        "view": {"type": "boolean", "description": "View collection"},
                        "progress": {"type": "boolean", "description": "Show progress"}
                    }
                }
            },
            {
                "name": "multi_clan_compare",
                "description": "Compare up to 5 clans side-by-side.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "clan": {"type": "array", "items": {"type": "string"}, "required": True, "description": "Clan names to compare (max 5)"},
                        "output": {"type": "string", "description": "Export to file (JSON/HTML/Markdown)"}
                    }
                }
            }
        ]
    
    def _run_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Run a CLI tool and return result with proper error handling."""
        try:
            tool_path = TOOLS_DIR / f"{tool_name}.py"
            if not tool_path.exists():
                return {"error": f"Tool not found: {tool_name}", "tool_path": str(tool_path)}
            
            # Build command based on tool
            cmd = [sys.executable, str(tool_path)]
            
            # Add arguments based on tool with proper type handling
            if tool_name == "runescape-api":
                if arguments.get("clan"):
                    cmd.extend(["--clan", str(arguments["clan"])])
                if arguments.get("player"):
                    cmd.extend(["--player", str(arguments["player"])])
                if arguments.get("item"):
                    cmd.extend(["--item", str(arguments["item"])])
                if arguments.get("item_id"):
                    cmd.extend(["--item-id", str(arguments["item_id"])])
                if arguments.get("game"):
                    cmd.extend(["--game", str(arguments["game"]).lower()])
            
            elif tool_name == "osrs-hiscores":
                cmd.extend(["--player", str(arguments.get("player", ""))])
                if arguments.get("game"):
                    cmd.extend(["--game", str(arguments["game"])])
                if arguments.get("skills_only") is True:
                    cmd.append("--skills")
                if arguments.get("activities_only") is True:
                    cmd.append("--activities")
            
            elif tool_name == "citadel-cap-tracker":
                cmd.extend(["--clan", str(arguments.get("clan", ""))])
                if arguments.get("since"):
                    cmd.extend(["--since", str(arguments["since"])])
            
            elif tool_name == "inactive-members":
                cmd.extend(["--clan", str(arguments.get("clan", ""))])
                if arguments.get("days"):
                    cmd.extend(["--days", str(arguments["days"])])
            
            elif tool_name == "player-lookup":
                cmd.extend(["--player", str(arguments.get("player", ""))])
                if arguments.get("game") == "osrs":
                    cmd.append("--osrs")
                if arguments.get("full") is True:
                    cmd.append("--full")
            
            elif tool_name == "price-alert":
                cmd.extend(["--item", str(arguments.get("item", ""))])
                if arguments.get("threshold"):
                    cmd.extend(["--threshold", str(arguments["threshold"])])
                if arguments.get("continuous") is True:
                    cmd.append("--continuous")
            
            elif tool_name == "ge-arbitrage":
                if arguments.get("scan_all") is True:
                    cmd.append("--scan-all")
                if arguments.get("min_profit"):
                    cmd.extend(["--min-profit", str(arguments["min_profit"])])
                if arguments.get("min_roi"):
                    cmd.extend(["--min-roi", str(arguments["min_roi"])])
            
            elif tool_name == "portfolio-tracker":
                action = arguments.get("action", "view")
                cmd.append(f"--{action}")
                if action == "add" and arguments.get("item"):
                    cmd.append(str(arguments["item"]))
                    if arguments.get("quantity"):
                        cmd.extend(["--quantity", str(arguments["quantity"])])
                    if arguments.get("buy_price"):
                        cmd.extend(["--buy-price", str(arguments["buy_price"])])
                elif action == "remove" and arguments.get("item"):
                    cmd.append(str(arguments["item"]))
            
            elif tool_name == "auto-report":
                cmd.extend(["--type", str(arguments.get("type", "daily"))])
                if arguments.get("clan"):
                    cmd.extend(["--clan", str(arguments["clan"])])
                if arguments.get("format"):
                    cmd.extend(["--format", str(arguments["format"])])
            
            elif tool_name == "advanced-trading":
                cmd.extend(["--strategy", str(arguments.get("strategy", "bulk-flip"))])
                if arguments.get("item"):
                    cmd.extend(["--item", str(arguments["item"])])
                if arguments.get("buy_price"):
                    cmd.extend(["--buy-price", str(arguments["buy_price"])])
                if arguments.get("sell_price"):
                    cmd.extend(["--sell-price", str(arguments["sell_price"])])
                if arguments.get("quantity"):
                    cmd.extend(["--quantity", str(arguments["quantity"])])
                if arguments.get("target_profit"):
                    cmd.extend(["--target-profit", str(arguments["target_profit"])])
                if arguments.get("margin"):
                    cmd.extend(["--margin", str(arguments["margin"])])
            
            elif tool_name == "pvp-loot-calculator":
                if arguments.get("kill") is True:
                    cmd.append("--kill")
                if arguments.get("loot"):
                    for item in arguments["loot"]:
                        cmd.extend(["--loot", str(item)])
                if arguments.get("risk"):
                    cmd.extend(["--risk", str(arguments["risk"])])
                if arguments.get("session") is True:
                    cmd.append("--session")
                if arguments.get("value"):
                    cmd.extend(["--value", str(arguments["value"])])
            
            elif tool_name == "collection-log":
                if arguments.get("add"):
                    cmd.extend(["--add", str(arguments["add"])])
                if arguments.get("category"):
                    cmd.extend(["--category", str(arguments["category"])])
                if arguments.get("source"):
                    cmd.extend(["--source", str(arguments["source"])])
                if arguments.get("view") is True:
                    cmd.append("--view")
                if arguments.get("progress") is True:
                    cmd.append("--progress")
            
            elif tool_name == "multi-clan-compare":
                clans = arguments.get("clan", [])
                for clan in clans:
                    cmd.extend(["--clan", str(clan)])
                if arguments.get("output"):
                    cmd.extend(["--output", str(arguments["output"])])
            
            # Always add --json flag
            cmd.append("--json")
            
            # Debug logging
            print(f"DEBUG: Running command: {' '.join(cmd)}", file=sys.stderr)
            
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Check for errors
            if result.returncode != 0:
                return {
                    "error": f"Tool execution failed",
                    "stderr": result.stderr,
                    "stdout": result.stdout[:500] if result.stdout else None,
                    "returncode": result.returncode
                }
            
            # Parse JSON output
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                return {
                    "error": f"Failed to parse JSON output",
                    "parse_error": str(e),
                    "stdout": result.stdout[:500] if result.stdout else None
                }
        
        except subprocess.TimeoutExpired:
            return {"error": "Tool execution timed out (60s)"}
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def handle_initialize(self, params: Dict) -> Dict:
        """Handle initialize request."""
        self.initialized = True
        return {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": self.SERVER_NAME,
                "version": self.SERVER_VERSION
            }
        }
    
    def handle_tools_list(self, params: Dict) -> Dict:
        """Handle tools/list request."""
        return {"tools": self.tools}
    
    def handle_tools_call(self, params: Dict) -> Dict:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Map MCP tool names to CLI tool names
        tool_map = {
            "runescape_api": "runescape-api",
            "osrs_hiscores": "osrs-hiscores",
            "citadel_tracker": "citadel-cap-tracker",
            "inactive_members": "inactive-members",
            "player_lookup": "player-lookup",
            "price_alert": "price-alert",
            "ge_arbitrage": "ge-arbitrage",
            "portfolio_tracker": "portfolio-tracker",
            "auto_report": "auto-report",
            "advanced_trading": "advanced-trading",
            "pvp_loot": "pvp-loot-calculator",
            "collection_log": "collection-log",
            "multi_clan_compare": "multi-clan-compare"
        }
        
        cli_tool_name = tool_map.get(tool_name, tool_name)
        
        print(f"DEBUG: Calling tool {tool_name} -> {cli_tool_name} with args: {arguments}", file=sys.stderr)
        
        result = self._run_tool(cli_tool_name, arguments)
        
        print(f"DEBUG: Tool result: {json.dumps(result, default=str)[:200]}", file=sys.stderr)
        
        response = {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2, default=str)
                }
            ]
        }
        if isinstance(result, dict) and "error" in result:
            response["isError"] = True
        return response
    
    def handle_request(self, request: Dict) -> Optional[Dict]:
        """Handle incoming MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = self.handle_initialize(params)
            elif method == "notifications/initialized":
                return None
            elif method == "tools/list":
                result = self.handle_tools_list(params)
            elif method == "tools/call":
                result = self.handle_tools_call(params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                    "traceback": traceback.format_exc()
                }
            }


def main():
    """Run MCP server with proper protocol."""
    server = RS_Agent_MCP_Server()

    # Process requests (persistent connection)
    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            response = server.handle_request(request)
            
            if response:
                print(json.dumps(response), flush=True)
        
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)
        
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
