#!/usr/bin/env python3
"""
Test script to debug Tavily API key issues
"""

import os
import requests
from dotenv import load_dotenv

def test_tavily_api():
    """Test Tavily API key and account status"""
    
    print("🔍 Testing Tavily API Configuration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("TAVILY_API_KEY")
    print(f"API Key: {'✓ Found' if api_key else '✗ Missing'}")
    
    if not api_key:
        print("❌ TAVILY_API_KEY is missing from .env file")
        return False
    
    # Show partial key for verification
    if len(api_key) > 10:
        masked_key = api_key[:8] + "..." + api_key[-4:]
        print(f"Key Preview: {masked_key}")
    
    # Test API connection
    print(f"\n🧪 Testing API Connection...")
    
    try:
        # Test with Tavily's search endpoint
        url = "https://api.tavily.com/search"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "api_key": api_key,
            "query": "test query",
            "max_results": 1
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Tavily API is working correctly!")
            result = response.json()
            print(f"   Results returned: {len(result.get('results', []))}")
            return True
            
        elif response.status_code == 401:
            print("❌ Unauthorized - API key issues:")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Raw response: {response.text}")
            
            print(f"\n💡 Possible solutions:")
            print(f"   1. Check if your API key is correct")
            print(f"   2. Verify your Tavily account is active")
            print(f"   3. Check if you have remaining API credits")
            print(f"   4. Try regenerating your API key")
            return False
            
        elif response.status_code == 429:
            print("❌ Rate limit exceeded")
            print("   Wait a moment and try again")
            return False
            
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - check your internet connection")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Error testing Tavily API: {e}")
        return False

def test_tavily_with_langchain():
    """Test Tavily integration with LangChain"""
    
    print(f"\n🔗 Testing Tavily with LangChain Integration")
    print("-" * 50)
    
    try:
        from tavily import TavilyClient
        
        api_key = os.getenv("TAVILY_API_KEY")
        client = TavilyClient(api_key=api_key)
        
        # Test search
        result = client.search("mathematics", max_results=1)
        
        if result and 'results' in result:
            print("✅ LangChain Tavily integration working!")
            print(f"   Found {len(result['results'])} results")
            return True
        else:
            print("❌ No results returned")
            return False
            
    except ImportError:
        print("❌ Tavily package not installed")
        print("   Run: pip install tavily-python")
        return False
    except Exception as e:
        print(f"❌ LangChain integration error: {e}")
        return False

def show_tavily_setup_guide():
    """Show setup guide for Tavily"""
    
    print(f"\n📋 Tavily Setup Guide")
    print("=" * 50)
    
    print(f"1. **Get API Key:**")
    print(f"   • Go to: https://app.tavily.com/")
    print(f"   • Sign up or log in")
    print(f"   • Navigate to API Keys section")
    print(f"   • Copy your API key")
    
    print(f"\n2. **Check Account Status:**")
    print(f"   • Verify your account is active")
    print(f"   • Check remaining API credits")
    print(f"   • Ensure no billing issues")
    
    print(f"\n3. **Update .env File:**")
    print(f"   • Add: TAVILY_API_KEY=\"your_api_key_here\"")
    print(f"   • Restart your server")
    
    print(f"\n4. **Alternative: Use MCP (if you have Tavily MCP URL):**")
    print(f"   • You mentioned having a Tavily MCP URL")
    print(f"   • This could be configured as an MCP server instead")
    print(f"   • Would you like help setting up MCP integration?")

if __name__ == "__main__":
    print("🚀 Tavily API Troubleshooting")
    print("=" * 60)
    
    # Test API directly
    api_works = test_tavily_api()
    
    # Test LangChain integration
    langchain_works = test_tavily_with_langchain()
    
    # Show setup guide
    show_tavily_setup_guide()
    
    print(f"\n" + "=" * 60)
    print(f"📊 Test Results:")
    print(f"   Direct API: {'✅ Working' if api_works else '❌ Issues'}")
    print(f"   LangChain: {'✅ Working' if langchain_works else '❌ Issues'}")
    
    if not api_works:
        print(f"\n⚠️  Tavily API needs attention")
        print(f"   The system will work without Tavily (using generated solutions)")
        print(f"   But web search functionality will be limited")
    else:
        print(f"\n🎉 Tavily is working correctly!")