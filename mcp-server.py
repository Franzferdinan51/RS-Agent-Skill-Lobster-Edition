#!/usr/bin/env python3
"""
RS-Agent MCP Server - Lobster Edition (Fixed)
=============================================
Proper MCP protocol implementation for RuneScape tools.

This server properly implements the MCP protocol including:
- initialize handshake
- tools/list
- tools/call
- Proper error handling

Usage:
    python3 mcp-server.py
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio

# Tools directory
TOOLS_DIR = Path(__file__).parent / "tools"


class MCPProtocolError(Exception):
    """MCP protocol error."""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"MCP error {code}: {message}")


class RS_Agent_MCP_Server:
    """Proper MCP Server implementation for RuneScape tools."""
    
    PROTOCOL_VERSION = "2024-11-05"
    SERVER_NAME = "rs-agent-mcp"
    SERVER_VERSION = "2.0.2"
    
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
        """Run a CLI tool and return result."""
        try:
            tool_path = TOOLS_DIR / f"{tool_name}.py"
            if not tool_path.exists():
                return {"error": f"Tool not found: {tool_name}"}
            
            # Build command based on tool
            cmd = [sys.executable, str(tool_path)]
            
            # Add arguments based on tool
            if tool_name == "runescape-api":
                if arguments.get("clan"):
                    cmd.extend(["--clan", arguments["clan"]])
                if arguments.get("player"):
                    cmd.extend(["--player", arguments["player"]])
                if arguments.get("item"):
                    cmd.extend(["--item", arguments["item"]])
                if arguments.get("item_id"):
                    cmd.extend(["--item-id", str(arguments["item_id"])])
                if arguments.get("game") == "osrs":
                    cmd.append("--osrs")
            
            elif tool_name == "osrs-hiscores":
                cmd.extend(["--player", arguments.get("player", "")])
                if arguments.get("game"):
                    cmd.extend(["--game", arguments["game"]])
            
            # Add --json flag for all tools
            cmd.append("--json")
            
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return {"error": result.stderr}
            
            try:
                return json.loads(result.stdout)
            except:
                return {"output": result.stdout}
        
        except subprocess.TimeoutExpired:
            return {"error": "Tool execution timed out (60s)"}
        except Exception as e:
            return {"error": str(e)}
    
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
        return {
            "tools": self.tools
        }
    
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
        result = self._run_tool(cli_tool_name, arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    def handle_request(self, request: Dict) -> Dict:
        """Handle incoming MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = self.handle_initialize(params)
            elif method == "notifications/initialized":
                # Just acknowledge, no response needed
                return None
            elif method == "tools/list":
                result = self.handle_tools_list(params)
            elif method == "tools/call":
                result = self.handle_tools_call(params)
            else:
                raise MCPProtocolError(-32601, f"Method not found: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        except MCPProtocolError as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "data": e.data
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }


def main():
    """Run MCP server with proper protocol."""
    server = RS_Agent_MCP_Server()
    
    # Send initialization response
    init_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": server.PROTOCOL_VERSION,
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": server.SERVER_NAME,
                "version": server.SERVER_VERSION
            }
        }
    }
    print(json.dumps(init_response), flush=True)
    
    # Process requests
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            
            if response:
                print(json.dumps(response), flush=True)
        
        except json.JSONDecodeError:
            continue
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
