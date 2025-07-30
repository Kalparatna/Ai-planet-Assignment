#!/usr/bin/env python3
"""
Tavily API Test Script
Tests if Tavily API is working properly for web search
"""

import os
import asyncio
import json
import time
from dotenv import load_dotenv
import aiohttp

# Load environment variables
load_dotenv()

async def test_tavily_api():
    """Test Tavily API functionality"""
    print("🧪 TESTING TAVILY API")
    print("=" * 50)
    
    # Check if API key exists
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_api_key:
        print("❌ TAVILY_API_KEY not found in environment variables")
        print("\n💡 To fix this:")
        print("1. Get your API key from: https://tavily.com")
        print("2. Add it to your .env file:")
        print("   TAVILY_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ Tavily API key found: {tavily_api_key[:10]}...{tavily_api_key[-5:]}")
    
    # Test basic API call
    print("\n🔍 Testing basic API call...")
    
    test_queries = [
        "what is 2+2",
        "area of circle formula",
        "solve quadratic equation step by step",
        "derivative of x squared"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        
        success = await test_single_query(tavily_api_key, query)
        
        if not success:
            print(f"❌ Test {i} failed")
        else:
            print(f"✅ Test {i} passed")
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    print("\n🎯 TAVILY API TEST COMPLETED")
    return True

async def test_single_query(api_key: str, query: str):
    """Test a single query with Tavily API"""
    try:
        start_time = time.time()
        
        # Prepare payload
        payload = {
            "api_key": api_key,
            "query": f"mathematical solution: {query}",
            "search_depth": "basic",
            "include_domains": [
                "mathsisfun.com",
                "khanacademy.org",
                "mathway.com"
            ],
            "max_results": 2,
            "include_answer": True,
            "include_raw_content": False
        }
        
        # Make API call
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.tavily.com/search",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                response_time = time.time() - start_time
                
                print(f"  Status Code: {response.status}")
                print(f"  Response Time: {response_time:.3f}s")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check response structure
                    if "results" in data:
                        results = data["results"]
                        print(f"  Results Found: {len(results)}")
                        
                        if results:
                            # Show first result
                            first_result = results[0]
                            title = first_result.get("title", "No title")
                            url = first_result.get("url", "No URL")
                            content = first_result.get("content", "No content")
                            
                            print(f"  First Result Title: {title[:60]}...")
                            print(f"  First Result URL: {url}")
                            print(f"  Content Length: {len(content)} characters")
                            print(f"  Content Preview: {content[:100]}...")
                            
                            # Check if content looks mathematical
                            math_indicators = ['=', 'formula', 'equation', 'solve', 'calculate', '+', '-', '×', '÷']
                            has_math = any(indicator in content.lower() for indicator in math_indicators)
                            
                            if has_math:
                                print("  ✅ Content appears mathematical")
                            else:
                                print("  ⚠️ Content may not be mathematical")
                            
                            return True
                        else:
                            print("  ⚠️ No results returned")
                            return False
                    else:
                        print("  ❌ Invalid response structure")
                        print(f"  Response keys: {list(data.keys())}")
                        return False
                
                elif response.status == 401:
                    print("  ❌ Authentication failed - check your API key")
                    return False
                
                elif response.status == 429:
                    print("  ❌ Rate limit exceeded - too many requests")
                    return False
                
                else:
                    error_text = await response.text()
                    print(f"  ❌ API Error: {response.status}")
                    print(f"  Error Details: {error_text[:200]}...")
                    return False
    
    except asyncio.TimeoutError:
        print("  ❌ Request timed out")
        return False
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

async def test_tavily_with_math_domains():
    """Test Tavily with specific math domains"""
    print("\n🧮 TESTING WITH MATH-SPECIFIC DOMAINS")
    print("-" * 50)
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        print("❌ No API key available")
        return
    
    # Test with math-specific domains
    math_domains = [
        "mathsisfun.com",
        "khanacademy.org", 
        "mathway.com",
        "symbolab.com",
        "wolframalpha.com"
    ]
    
    query = "how to solve quadratic equations"
    
    payload = {
        "api_key": tavily_api_key,
        "query": query,
        "search_depth": "advanced",
        "include_domains": math_domains,
        "max_results": 3,
        "include_answer": True,
        "include_raw_content": True
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.tavily.com/search",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    
                    print(f"✅ Found {len(results)} results from math domains")
                    
                    for i, result in enumerate(results, 1):
                        url = result.get("url", "")
                        title = result.get("title", "")
                        content = result.get("content", "")
                        
                        print(f"\nResult {i}:")
                        print(f"  URL: {url}")
                        print(f"  Title: {title[:80]}...")
                        print(f"  Content: {content[:150]}...")
                        
                        # Check which domain
                        domain_found = None
                        for domain in math_domains:
                            if domain in url:
                                domain_found = domain
                                break
                        
                        if domain_found:
                            print(f"  ✅ From trusted math domain: {domain_found}")
                        else:
                            print(f"  ⚠️ From other domain")
                
                else:
                    print(f"❌ Request failed with status: {response.status}")
    
    except Exception as e:
        print(f"❌ Error testing math domains: {e}")

async def test_connection_manager():
    """Test if connection manager works with Tavily"""
    print("\n🔗 TESTING CONNECTION MANAGER")
    print("-" * 50)
    
    try:
        from services.connection_manager import connection_manager
        
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            print("❌ No API key available")
            return
        
        payload = {
            "api_key": tavily_api_key,
            "query": "test math query",
            "max_results": 1,
            "include_answer": True
        }
        
        print("🔍 Testing connection manager...")
        
        result = await connection_manager.post_json(
            "https://api.tavily.com/search",
            payload,
            timeout=10
        )
        
        if result and "results" in result:
            print("✅ Connection manager working correctly")
            print(f"Results: {len(result['results'])}")
        else:
            print("⚠️ Connection manager returned unexpected result")
            print(f"Result keys: {list(result.keys()) if result else 'None'}")
    
    except Exception as e:
        print(f"❌ Connection manager error: {e}")

async def test_web_search_service():
    """Test the actual web search service"""
    print("\n🌐 TESTING WEB SEARCH SERVICE")
    print("-" * 50)
    
    try:
        from services.web_search import WebSearchService
        
        web_service = WebSearchService()
        
        if not web_service.tavily_api_key:
            print("❌ Web service has no Tavily API key")
            return
        
        print("🔍 Testing web search service...")
        
        test_query = "what is the derivative of x squared"
        result = await web_service.search(test_query)
        
        if result and result.get("found"):
            print("✅ Web search service working")
            print(f"Solution: {result.get('solution', '')[:200]}...")
            print(f"Confidence: {result.get('confidence', 0)}")
            print(f"References: {result.get('references', [])}")
        else:
            print("❌ Web search service returned no results")
            print(f"Result: {result}")
    
    except Exception as e:
        print(f"❌ Web search service error: {e}")

def check_env_file():
    """Check .env file configuration"""
    print("\n📁 CHECKING .ENV FILE")
    print("-" * 50)
    
    env_file = ".env"
    if os.path.exists(env_file):
        print("✅ .env file exists")
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        if "TAVILY_API_KEY" in content:
            print("✅ TAVILY_API_KEY found in .env file")
            
            # Check if it's not empty
            tavily_key = os.getenv("TAVILY_API_KEY")
            if tavily_key and len(tavily_key) > 10:
                print("✅ API key appears to be valid length")
            else:
                print("⚠️ API key may be empty or too short")
        else:
            print("❌ TAVILY_API_KEY not found in .env file")
            print("💡 Add this line to your .env file:")
            print("TAVILY_API_KEY=your_api_key_here")
    else:
        print("❌ .env file not found")
        print("💡 Create a .env file with:")
        print("TAVILY_API_KEY=your_api_key_here")

async def main():
    """Main test function"""
    check_env_file()
    await test_tavily_api()
    await test_tavily_with_math_domains()
    await test_connection_manager()
    await test_web_search_service()
    
    print("\n🎯 SUMMARY")
    print("=" * 50)
    print("If all tests passed, your Tavily API is working correctly!")
    print("If any tests failed, check:")
    print("1. Your API key is correct")
    print("2. You have internet connection")
    print("3. You haven't exceeded rate limits")
    print("4. The API service is not down")

if __name__ == "__main__":
    asyncio.run(main())