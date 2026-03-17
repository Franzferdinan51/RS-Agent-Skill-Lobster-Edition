#!/usr/bin/env python3
"""
RS-Agent MCP Server - Lobster Edition
=====================================
Model Context Protocol (MCP) server for RuneScape tools.

Allows LM Studio and other MCP clients to access all RuneScape tools.

Features:
- All 9 CLI tools exposed as MCP tools
- Real-time GE data access
- Clan management
- Portfolio tracking
- OSRS and RS3 support
- Automated reports

Usage:
    python3 mcp-server.py
    
LM Studio Configuration:
    Add to LM Studio MCP settings:
    {
      "mcpServers": {
        "runescape": {
          "command": "python3",
          "args": ["/path/to/mcp-server.py"],
          "cwd": "/path/to/rs-agent-tools"
        }
      }
    }
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

# MCP Server Implementation
class RS_Agent_MCP_Server:
    """MCP Server for RuneScape tools."""
    
    def __init__(self):
        self.tools_dir = Path(__file__).parent
        self.tools = self._register_tools()
    
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
                "description": "Lookup Old School RuneScape player hiscores and activity data.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "player": {"type": "string", "description": "Player name", "required": True},
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
            }
        ]
    
    def _run_tool(self, tool_name: str, args: List[str]) -> Dict:
        """Run a CLI tool and return result."""
        try:
            tool_path = self.tools_dir / "tools" / f"{tool_name}.py"
            if not tool_path.exists():
                return {"error": f"Tool not found: {tool_name}"}
            
            cmd = ["python3", str(tool_path)] + args + ["--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return {"error": result.stderr}
            
            try:
                return json.loads(result.stdout)
            except:
                return {"output": result.stdout}
        
        except subprocess.TimeoutExpired:
            return {"error": "Tool execution timed out"}
        except Exception as e:
            return {"error": str(e)}
    
    def handle_tool_call(self, tool_name: str, arguments: Dict) -> Dict:
        """Handle MCP tool call."""
        
        if tool_name == "runescape_api":
            args = []
            if arguments.get("clan"):
                args.extend(["--clan", arguments["clan"]])
            if arguments.get("player"):
                args.extend(["--player", arguments["player"]])
            if arguments.get("item"):
                args.extend(["--item", arguments["item"]])
            if arguments.get("item_id"):
                args.extend(["--item-id", str(arguments["item_id"])])
            if arguments.get("game") == "osrs":
                args.append("--osrs")
            return self._run_tool("runescape-api", args)
        
        elif tool_name == "osrs_hiscores":
            args = ["--player", arguments["player"]]
            if arguments.get("skills_only"):
                args.append("--skills")
            if arguments.get("activities_only"):
                args.append("--activities")
            return self._run_tool("osrs-hiscores", args)
        
        elif tool_name == "citadel_tracker":
            args = ["--clan", arguments["clan"], "--since", arguments.get("since", "2026-03-11")]
            return self._run_tool("citadel-cap-tracker", args)
        
        elif tool_name == "inactive_members":
            args = ["--clan", arguments["clan"], "--days", str(arguments.get("days", 90))]
            return self._run_tool("inactive-members", args)
        
        elif tool_name == "player_lookup":
            args = ["--player", arguments["player"]]
            if arguments.get("game") == "osrs":
                args.append("--osrs")
            if arguments.get("full"):
                args.append("--full")
            return self._run_tool("player-lookup", args)
        
        elif tool_name == "price_alert":
            args = ["--item", arguments["item"], "--threshold", str(arguments["threshold"])]
            if arguments.get("continuous"):
                args.append("--continuous")
            return self._run_tool("price-alert", args)
        
        elif tool_name == "ge_arbitrage":
            args = []
            if arguments.get("scan_all"):
                args.append("--scan-all")
            args.extend(["--min-profit", str(arguments.get("min_profit", 10000))])
            args.extend(["--min-roi", str(arguments.get("min_roi", 1.0))])
            return self._run_tool("ge-arbitrage", args)
        
        elif tool_name == "portfolio_tracker":
            action = arguments.get("action", "view")
            args = [f"--{action}"]
            
            if action == "add" and arguments.get("item"):
                args.extend([arguments["item"]])
                if arguments.get("quantity"):
                    args.extend(["--quantity", str(arguments["quantity"])])
                if arguments.get("buy_price"):
                    args.extend(["--buy-price", str(arguments["buy_price"])])
            elif action == "remove" and arguments.get("item"):
                args.append(arguments["item"])
            
            return self._run_tool("portfolio-tracker", args)
        
        elif tool_name == "auto_report":
            args = ["--type", arguments["type"], "--format", arguments.get("format", "html")]
            if arguments.get("clan"):
                args.extend(["--clan", arguments["clan"]])
            return self._run_tool("auto-report", args)
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}


def main():
    """Run MCP server."""
    server = RS_Agent_MCP_Server()
    
    print(json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "rs-agent-mcp",
                "version": "1.0.0"
            }
        }
    }), flush=True)
    
    # Read and process MCP requests
    for line in sys.stdin:
        try:
            request = json.loads(line)
            
            if request.get("method") == "tools/list":
                # Return available tools
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": server.tools
                    }
                }
                print(json.dumps(response), flush=True)
            
            elif request.get("method") == "tools/call":
                # Call a tool
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = server.handle_tool_call(tool_name, arguments)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
                print(json.dumps(response), flush=True)
            
            else:
                # Unknown method
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {request.get('method')}"
                    }
                }
                print(json.dumps(response), flush=True)
        
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
