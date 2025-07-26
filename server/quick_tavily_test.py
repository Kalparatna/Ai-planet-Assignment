#!/usr/bin/env python3
"""
Quick test for Tavily API key
"""

import os
import requests
from dotenv import load_dotenv

def quick_tavily_test():
    """Quick test of Tavily API key"""
    
    print("🔍 Quick Tavily API Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("TAVILY_API_KEY")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    
    if api_key:
        print(f"Key starts with: {api_key[:10]}...")
        print(f"Key length: {len(api_key)} characters")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    # Test the API
    print(f"\n🧪 Testing API...")
    
    try:
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": "mathematics",
            "max_results": 1
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API key is working!")
            return True
        elif response.status_code == 401:
            print("❌ API key is invalid or expired")
            try:
                error = response.json()
                print(f"Error details: {error}")
            except:
                print(f"Raw error: {response.text}")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if quick_tavily_test():
        print(f"\n🎉 Your Tavily API key is working!")
        print(f"The 401 error might be a temporary issue.")
    else:
        print(f"\n⚠️  API key needs attention")
        print(f"Options:")
        print(f"1. Get a new API key from https://app.tavily.com/")
        print(f"2. Use MCP integration instead")
        print(f"3. System works fine without Tavily (uses generated solutions)")