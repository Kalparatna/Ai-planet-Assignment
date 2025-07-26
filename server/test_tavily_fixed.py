#!/usr/bin/env python3
"""
Test the fixed Tavily API integration
"""

import os
import requests
import asyncio
from dotenv import load_dotenv
from services.web_search import WebSearchService

def test_tavily_direct():
    """Test Tavily API directly with correct format"""
    
    print("🧪 Testing Tavily API Direct Call")
    print("=" * 50)
    
    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key:
        print("❌ No Tavily API key found")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test with the correct Tavily API format
    payload = {
        "api_key": api_key,
        "query": "solve quadratic equation x^2 - 5x + 6 = 0",
        "search_depth": "basic",
        "max_results": 3,
        "include_answer": True
    }
    
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Tavily API is working!")
            print(f"   Results found: {len(result.get('results', []))}")
            
            if result.get('results'):
                first_result = result['results'][0]
                print(f"   First result URL: {first_result.get('url', 'N/A')}")
                print(f"   Content preview: {first_result.get('content', '')[:100]}...")
            
            return True
            
        elif response.status_code == 401:
            print("❌ Unauthorized - API key issue")
            try:
                error = response.json()
                print(f"   Error details: {error}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_web_search_service():
    """Test the WebSearchService with fixed Tavily integration"""
    
    print(f"\n🔍 Testing WebSearchService")
    print("=" * 50)
    
    try:
        web_search = WebSearchService()
        
        # Test search
        result = await web_search.search("What is 2 + 2?")
        
        if result.get("found"):
            print("✅ Web search service is working!")
            print(f"   Source: Web Search")
            print(f"   Confidence: {result.get('confidence', 0)}")
            print(f"   References: {len(result.get('references', []))}")
            print(f"   Solution preview: {result.get('solution', '')[:200]}...")
            return True
        else:
            print("❌ Web search didn't find results")
            return False
            
    except Exception as e:
        print(f"❌ Error in web search service: {e}")
        return False

async def test_math_routing():
    """Test the complete math routing with web search"""
    
    print(f"\n🧮 Testing Complete Math Routing")
    print("=" * 50)
    
    try:
        # Test with a query that should trigger web search
        import requests
        
        response = requests.post(
            "http://localhost:8000/math/solve",
            json={"query": "How do you solve a quadratic equation using the quadratic formula?"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Math routing is working!")
            print(f"   Source: {result.get('source')}")
            print(f"   Confidence: {result.get('confidence')}")
            
            # Check if it used web search
            if result.get('source') == 'web_search':
                print("✅ Web search was used successfully!")
            else:
                print(f"ℹ️  Used {result.get('source')} instead of web search")
            
            return True
        else:
            print(f"❌ Math routing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running - start with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error in math routing test: {e}")
        return False

def show_tavily_status():
    """Show current Tavily integration status"""
    
    print(f"\n📊 Tavily Integration Status")
    print("=" * 50)
    
    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY")
    
    print(f"API Key: {'✅ Set' if api_key else '❌ Missing'}")
    
    if api_key:
        print(f"Key format: {api_key[:4]}...{api_key[-4:]} ({len(api_key)} chars)")
    
    print(f"\n🔧 Integration Details:")
    print(f"   • Using direct Tavily API (not MCP)")
    print(f"   • Correct API endpoint: https://api.tavily.com/search")
    print(f"   • API key in payload (not headers)")
    print(f"   • Enhanced queries for math context")
    print(f"   • Fallback to web scraping if Tavily fails")
    print(f"   • Fallback to generated solutions if all fails")

async def main():
    """Main test function"""
    
    print("🚀 Testing Fixed Tavily Integration")
    print("=" * 80)
    
    # Show current status
    show_tavily_status()
    
    # Test direct API
    direct_ok = test_tavily_direct()
    
    # Test web search service
    service_ok = await test_web_search_service()
    
    # Test complete routing (only if server is running)
    routing_ok = await test_math_routing()
    
    print(f"\n" + "=" * 80)
    print(f"📋 Test Results:")
    print(f"   Direct Tavily API: {'✅ Working' if direct_ok else '❌ Issues'}")
    print(f"   Web Search Service: {'✅ Working' if service_ok else '❌ Issues'}")
    print(f"   Math Routing: {'✅ Working' if routing_ok else '❌ Issues/Server not running'}")
    
    if direct_ok and service_ok:
        print(f"\n🎉 Tavily integration is working!")
        print(f"   Your math routing agent can now use web search")
        print(f"   No more 401 Unauthorized errors")
    elif direct_ok:
        print(f"\n⚠️  Tavily API works, but service integration has issues")
    else:
        print(f"\n❌ Tavily API still has issues")
        print(f"   Check your API key at: https://app.tavily.com/")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. If tests pass: Restart your server (python main.py)")
    print(f"   2. Test math queries in your UI")
    print(f"   3. Check server logs for 'Tavily API error' messages")
    print(f"   4. Web search should now work without 401 errors")

if __name__ == "__main__":
    asyncio.run(main())