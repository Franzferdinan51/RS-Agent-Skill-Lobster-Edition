#!/usr/bin/env python3
"""
Simple Fetch MCP Server - Lobster Edition (Fixed)
=================================================
A working fetch MCP server that properly implements the MCP protocol.

Unlike the broken @modelcontextprotocol/server-fetch, this server:
- Maintains persistent stdio connection
- Properly handles initialize handshake
- Doesn't exit after first response
- Has proper error handling

Usage:
    python3 fetch-mcp-server.py
"""

import json
import sys
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


class SimpleFetchMCPServer:
    """Simple, working fetch MCP server."""
    
    PROTOCOL_VERSION = "2024-11-05"
    SERVER_NAME = "simple-fetch-mcp"
    SERVER_VERSION = "1.0.0"
    
    def __init__(self):
        self.initialized = False
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; SimpleFetchMCP/1.0)"
        })
    
    def get_tools(self) -> list:
        """Return available tools."""
        return [
            {
                "name": "fetch",
                "description": "Fetch web content and convert to markdown. Works with most websites.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to fetch",
                            "required": True
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Request timeout in seconds",
                            "default": 30
                        },
                        "markdown": {
                            "type": "boolean",
                            "description": "Convert to markdown",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "fetch_json",
                "description": "Fetch JSON data from an API endpoint.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to fetch JSON from",
                            "required": True
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Request timeout in seconds",
                            "default": 30
                        }
                    }
                }
            },
            {
                "name": "fetch_text",
                "description": "Fetch plain text from a URL.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to fetch text from",
                            "required": True
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Request timeout in seconds",
                            "default": 30
                        }
                    }
                }
            }
        ]
    
    def fetch_url(self, url: str, timeout: int = 30, as_markdown: bool = True) -> Dict[str, Any]:
        """Fetch URL and return content."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'application/json' in content_type:
                return {
                    "success": True,
                    "content": response.json(),
                    "content_type": "json",
                    "url": url,
                    "status_code": response.status_code
                }
            elif 'text/html' in content_type:
                if as_markdown:
                    # Simple HTML to markdown conversion
                    html = response.text
                    markdown = self._html_to_markdown(html)
                    return {
                        "success": True,
                        "content": markdown,
                        "content_type": "markdown",
                        "url": url,
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "success": True,
                        "content": response.text,
                        "content_type": "html",
                        "url": url,
                        "status_code": response.status_code
                    }
            else:
                return {
                    "success": True,
                    "content": response.text,
                    "content_type": "text",
                    "url": url,
                    "status_code": response.status_code
                }
        
        except requests.Timeout:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds",
                "url": url
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def _html_to_markdown(self, html: str) -> str:
        """Simple HTML to markdown conversion."""
        import re
        
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert headers
        html = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert links
        html = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert bold and italic
        html = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert lists
        html = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert line breaks
        html = re.sub(r'<br[^>]*>', '\n', html, flags=re.IGNORECASE)
        
        # Remove all other HTML tags
        markdown = re.sub(r'<[^>]+>', '', html)
        
        # Clean up whitespace
        markdown = re.sub(r'\n\s*\n', '\n\n', markdown)
        markdown = markdown.strip()
        
        return markdown
    
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
            "tools": self.get_tools()
        }
    
    def handle_tools_call(self, params: Dict) -> Dict:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "fetch":
            url = arguments.get("url", "")
            timeout = arguments.get("timeout", 30)
            markdown = arguments.get("markdown", True)
            
            if not url:
                result = {"error": "URL is required"}
            else:
                result = self.fetch_url(url, timeout, markdown)
        
        elif tool_name == "fetch_json":
            url = arguments.get("url", "")
            timeout = arguments.get("timeout", 30)
            
            if not url:
                result = {"error": "URL is required"}
            else:
                result = self.fetch_url(url, timeout, as_markdown=False)
                if result.get("success"):
                    try:
                        result["content"] = json.loads(result["content"])
                        result["content_type"] = "json"
                    except:
                        result["success"] = False
                        result["error"] = "Response is not valid JSON"
        
        elif tool_name == "fetch_text":
            url = arguments.get("url", "")
            timeout = arguments.get("timeout", 30)
            
            if not url:
                result = {"error": "URL is required"}
            else:
                result = self.fetch_url(url, timeout, as_markdown=False)
        
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2, default=str)
                }
            ]
        }
    
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
                    "message": f"Internal error: {str(e)}"
                }
            }


def main():
    """Run the fetch MCP server."""
    server = SimpleFetchMCPServer()
    
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
