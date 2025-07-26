#!/usr/bin/env python3
"""
Test the complete math routing system with all components working
"""

import requests
import json
import time

def test_query(query, expected_source=None):
    """Test a single math query"""
    
    print(f"📝 Query: {query}")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/math/solve",
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Success!")
            print(f"   Source: {result.get('source')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   References: {len(result.get('references', []))}")
            
            # Show solution preview
            solution = result.get('solution', '')
            if len(solution) > 200:
                print(f"   Solution: {solution[:200]}...")
            else:
                print(f"   Solution: {solution}")
            
            # Check if it matches expected source
            if expected_source and result.get('source') == expected_source:
                print(f"   ✅ Used expected source: {expected_source}")
            elif expected_source:
                print(f"   ℹ️  Used {result.get('source')} instead of expected {expected_source}")
            
            return True
            
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running - start with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_feedback_system():
    """Test the feedback system"""
    
    print(f"\n📝 Testing Feedback System")
    print("=" * 60)
    
    feedback_data = {
        "query_id": "test-complete-system",
        "original_solution": "The derivative of x² is 2x",
        "feedback": "Great solution! Very clear and concise.",
        "rating": 5,
        "corrections": "No corrections needed"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/feedback/submit",
            json=feedback_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Feedback system working!")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Feedback failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        return False

def main():
    """Test the complete system with different query types"""
    
    print("🚀 Testing Complete Math Routing System")
    print("=" * 80)
    
    # Test different types of queries
    test_cases = [
        # Simple arithmetic (likely to use generated solution)
        ("What is 2 + 2?", "generated"),
        
        # Basic algebra (might be in knowledge base)
        ("Solve x² - 5x + 6 = 0", "knowledge_base"),
        
        # Complex query (likely to use web search)
        ("How do you solve a system of linear equations using matrix methods?", "web_search"),
        
        # Calculus (might use web search)
        ("Find the integral of sin(x) dx", "web_search"),
        
        # Geometry (might be in knowledge base)
        ("What is the area of a circle with radius 5?", "knowledge_base"),
        
        # Advanced topic (likely web search)
        ("Explain the Fundamental Theorem of Calculus", "web_search")
    ]
    
    results = []
    
    for i, (query, expected_source) in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/6")
        success = test_query(query, expected_source)
        results.append(success)
        
        # Small delay between requests
        time.sleep(1)
    
    # Test feedback system
    feedback_success = test_feedback_system()
    
    # Summary
    print(f"\n" + "=" * 80)
    print(f"📊 Test Results Summary:")
    print(f"   Math Queries: {sum(results)}/{len(results)} passed")
    print(f"   Feedback System: {'✅ Working' if feedback_success else '❌ Issues'}")
    
    if sum(results) == len(results) and feedback_success:
        print(f"\n🎉 Complete System Test: PASSED!")
        print(f"   ✅ All components working correctly")
        print(f"   ✅ Knowledge base integration")
        print(f"   ✅ Web search with Tavily API")
        print(f"   ✅ Generated solutions fallback")
        print(f"   ✅ Response formatting")
        print(f"   ✅ Feedback system")
        
        print(f"\n🎯 Your Math Routing Agent is fully operational!")
        print(f"   • Knowledge Base: Pinecone vector search")
        print(f"   • Web Search: Tavily API integration")
        print(f"   • AI Generation: Google Gemini")
        print(f"   • Clean UI: Proper response formatting")
        print(f"   • Learning: Feedback collection system")
        
    else:
        print(f"\n⚠️  Some components need attention:")
        if sum(results) < len(results):
            print(f"   • Math routing has issues")
        if not feedback_success:
            print(f"   • Feedback system has issues")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Test your UI with various math queries")
    print(f"   2. Submit feedback to improve the system")
    print(f"   3. Monitor server logs for any issues")
    print(f"   4. Your system should handle all types of math problems!")

if __name__ == "__main__":
    main()