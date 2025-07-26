#!/usr/bin/env python3
"""
Comprehensive system status check
"""

import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

def check_environment_variables():
    """Check all required environment variables"""
    
    print("🔧 Environment Variables")
    print("-" * 30)
    
    load_dotenv()
    
    required_vars = {
        "GOOGLE_API_KEY": "Google Gemini API",
        "TAVILY_API_KEY": "Tavily Search API", 
        "PINECONE_API_KEY": "Pinecone Vector DB",
        "PINECONE_INDEX_NAME": "Pinecone Index Name",
        "PINECONE_ENVIRONMENT": "Pinecone Environment",
        "PINECONE_CLOUD": "Pinecone Cloud Provider"
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set ({description})")
        else:
            print(f"❌ {var}: Missing ({description})")
            all_good = False
    
    return all_good

def check_mcp_configuration():
    """Check MCP configuration"""
    
    print(f"\n🔗 MCP Configuration")
    print("-" * 30)
    
    mcp_path = Path(".kiro/settings/mcp.json")
    
    if not mcp_path.exists():
        print("❌ MCP configuration not found")
        return False
    
    try:
        with open(mcp_path, 'r') as f:
            mcp_config = json.load(f)
        
        servers = mcp_config.get("mcpServers", {})
        print(f"✅ MCP config found with {len(servers)} servers")
        
        if "tavily-search" in servers:
            tavily_config = servers["tavily-search"]
            print(f"✅ Tavily MCP server configured")
            
            api_key = tavily_config.get("env", {}).get("TAVILY_API_KEY", "")
            if api_key:
                print(f"✅ Tavily API key set in MCP config")
            else:
                print(f"❌ Tavily API key missing in MCP config")
                return False
        else:
            print(f"❌ Tavily MCP server not configured")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading MCP config: {e}")
        return False

def check_api_connectivity():
    """Check API connectivity"""
    
    print(f"\n🌐 API Connectivity")
    print("-" * 30)
    
    # Test Tavily API
    api_key = os.getenv("TAVILY_API_KEY")
    if api_key:
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": api_key, "query": "test", "max_results": 1},
                timeout=5
            )
            if response.status_code == 200:
                print("✅ Tavily API: Working")
            elif response.status_code == 401:
                print("❌ Tavily API: Unauthorized (check API key)")
            else:
                print(f"⚠️  Tavily API: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Tavily API: Connection error ({e})")
    else:
        print("❌ Tavily API: No API key")
    
    # Test Pinecone (basic connection)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    if pinecone_key:
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=pinecone_key)
            indexes = pc.list_indexes()
            print(f"✅ Pinecone: Connected ({len(indexes.names())} indexes)")
        except Exception as e:
            print(f"❌ Pinecone: Connection error ({e})")
    else:
        print("❌ Pinecone: No API key")

def check_required_packages():
    """Check required packages"""
    
    print(f"\n📦 Required Packages")
    print("-" * 30)
    
    packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pinecone", "Pinecone client"),
        ("langchain_pinecone", "LangChain Pinecone integration"),
        ("langchain_google_genai", "Google Gemini integration"),
        ("tavily", "Tavily search client"),
        ("requests", "HTTP client"),
        ("python-dotenv", "Environment variables")
    ]
    
    all_installed = True
    for package, description in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}: Installed ({description})")
        except ImportError:
            print(f"❌ {package}: Missing ({description})")
            all_installed = False
    
    return all_installed

def check_data_directories():
    """Check data directories"""
    
    print(f"\n📁 Data Directories")
    print("-" * 30)
    
    directories = [
        ("data", "Main data directory"),
        ("data/vectordb", "Vector database storage"),
        (".kiro", "Kiro configuration"),
        (".kiro/settings", "Kiro settings")
    ]
    
    for dir_path, description in directories:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}: Exists ({description})")
        else:
            print(f"⚠️  {dir_path}: Missing ({description})")
            os.makedirs(dir_path, exist_ok=True)
            print(f"   Created {dir_path}")

def main():
    """Main status check"""
    
    print("🚀 System Status Check")
    print("=" * 60)
    
    # Run all checks
    env_ok = check_environment_variables()
    mcp_ok = check_mcp_configuration()
    packages_ok = check_required_packages()
    check_api_connectivity()
    check_data_directories()
    
    print(f"\n" + "=" * 60)
    print(f"📊 Overall Status:")
    print(f"   Environment Variables: {'✅ Good' if env_ok else '❌ Issues'}")
    print(f"   MCP Configuration: {'✅ Good' if mcp_ok else '❌ Issues'}")
    print(f"   Required Packages: {'✅ Good' if packages_ok else '❌ Issues'}")
    
    if env_ok and mcp_ok and packages_ok:
        print(f"\n🎉 System is ready!")
        print(f"   You can start your server: python main.py")
        print(f"   Both direct API and MCP integration should work")
    else:
        print(f"\n⚠️  System needs attention")
        print(f"   Fix the issues above before starting the server")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Fix any issues shown above")
    print(f"   2. Start server: python main.py")
    print(f"   3. Test with: curl -X POST http://localhost:8000/math/solve -H 'Content-Type: application/json' -d '{\"query\":\"What is 2+2?\"}'")
    print(f"   4. Check Kiro MCP panel for Tavily connection status")

if __name__ == "__main__":
    main()