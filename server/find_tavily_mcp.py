#!/usr/bin/env python3
"""
Find and setup the correct Tavily MCP server
"""

import subprocess
import json
from pathlib import Path

def search_for_tavily_mcp():
    """Search for available Tavily MCP packages"""
    
    print("🔍 Searching for Tavily MCP Packages")
    print("=" * 50)
    
    # Common Tavily MCP package names to try
    possible_packages = [
        "tavily-mcp-server",
        "mcp-server-tavily", 
        "tavily-mcp",
        "mcp-tavily",
        "tavily-search-mcp",
        "mcp-search-tavily"
    ]
    
    print("🧪 Testing possible package names...")
    
    for package in possible_packages:
        try:
            result = subprocess.run(
                ["uvx", package, "--help"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Found working package: {package}")
                return package
            else:
                print(f"❌ {package}: Not found")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {package}: Timeout (might work but slow)")
        except Exception as e:
            print(f"❌ {package}: Error ({e})")
    
    print(f"\n⚠️  No standard Tavily MCP packages found")
    return None

def check_mcp_registry():
    """Check what MCP servers are available"""
    
    print(f"\n📋 Checking Available MCP Servers")
    print("-" * 40)
    
    try:
        # Try to list available MCP servers
        result = subprocess.run(
            ["uvx", "--help"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ UVX is working")
        else:
            print("❌ UVX has issues")
            
    except Exception as e:
        print(f"❌ Error checking UVX: {e}")

def create_custom_tavily_mcp():
    """Create a custom Tavily MCP server script"""
    
    print(f"\n🛠️  Creating Custom Tavily MCP Server")
    print("-" * 40)
    
    # Create a simple MCP server script for Tavily
    mcp_server_code = '''#!/usr/bin/env python3
"""
Custom Tavily MCP Server
"""

import json
import sys
import os
from typing import Dict, Any, List
import requests

class TavilyMCPServer:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search using Tavily API"""
        
        if not self.api_key:
            return {"error": "TAVILY_API_KEY not set"}
        
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "search":
            query = params.get("query", "")
            max_results = params.get("max_results", 5)
            return self.search(query, max_results)
        else:
            return {"error": f"Unknown method: {method}"}

def main():
    """Main MCP server function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Custom Tavily MCP Server")
        print("Usage: python custom_tavily_mcp.py")
        print("Environment: TAVILY_API_KEY required")
        return
    
    server = TavilyMCPServer()
    
    # Simple test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        result = server.search("test query", 1)
        print(json.dumps(result, indent=2))
        return
    
    print("Custom Tavily MCP Server started")
    print("Set TAVILY_API_KEY environment variable")
    
    # In a real MCP server, this would handle JSON-RPC requests
    # For now, just indicate it's running
    while True:
        try:
            line = input()
            if line.strip() == "quit":
                break
        except KeyboardInterrupt:
            break
    
    print("Server stopped")

if __name__ == "__main__":
    main()
'''
    
    # Save the custom MCP server
    with open("custom_tavily_mcp.py", "w") as f:
        f.write(mcp_server_code)
    
    print("✅ Created custom_tavily_mcp.py")