#!/usr/bin/env python3
"""
Test script to verify feedback system is working
"""

import requests
import json

def test_feedback_submission():
    """Test the feedback submission endpoint"""
    
    print("🧪 Testing Feedback Submission")
    print("=" * 50)
    
    # Test data
    feedback_data = {
        "query_id": "test-123",
        "original_solution": "**Problem:** Find the derivative of x^2\n\n**Solution:**\n\nThe derivative is 2x",
        "feedback": "The solution is correct but could use more detailed steps",
        "rating": 4,
        "corrections": "Please show the power rule application step by step"
    }
    
    try:
        # Submit feedback
        print("📤 Submitting feedback...")
        response = requests.post(
            "http://localhost:8000/feedback/submit",
            json=feedback_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Feedback submitted successfully!")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            if result.get('improved_solution'):
                print(f"   Improved Solution: {result.get('improved_solution')[:100]}...")
        else:
            print(f"❌ Feedback submission failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure your server is running: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error testing feedback: {e}")
        return False
    
    return True

def test_feedback_stats():
    """Test the feedback stats endpoint"""
    
    print("\n📊 Testing Feedback Stats")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/feedback/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats retrieved successfully!")
            print(f"   Total Feedback: {stats.get('total_feedback', 0)}")
            print(f"   Average Rating: {stats.get('average_rating', 0)}")
            print(f"   Total Improvements: {stats.get('total_improvements', 0)}")
            print(f"   Ratings Distribution: {stats.get('ratings_distribution', {})}")
        else:
            print(f"❌ Stats retrieval failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return False
    
    return True

def test_math_solve():
    """Test the math solve endpoint to get a solution for feedback testing"""
    
    print("\n🔢 Testing Math Solve (for feedback testing)")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/math/solve",
            json={"query": "Find the derivative of x^3 + 2x^2"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Math solution generated!")
            print(f"   Source: {result.get('source')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Solution Preview: {result.get('solution', '')[:150]}...")
            return result
        else:
            print(f"❌ Math solve failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing math solve: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testing Feedback System")
    print("=" * 60)
    
    # Test math solve first
    math_result = test_math_solve()
    
    # Test feedback submission
    feedback_success = test_feedback_submission()
    
    # Test feedback stats
    stats_success = test_feedback_stats()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Math Solve: {'✅ Working' if math_result else '❌ Failed'}")
    print(f"   Feedback Submit: {'✅ Working' if feedback_success else '❌ Failed'}")
    print(f"   Feedback Stats: {'✅ Working' if stats_success else '❌ Failed'}")
    
    if feedback_success:
        print("\n🎉 Feedback system is working!")
        print("\nYou can now:")
        print("1. Submit feedback through your UI")
        print("2. View feedback stats at /feedback/stats")
        print("3. Check saved feedback in data/feedback.json")
    else:
        print("\n⚠️  Feedback system needs attention")
        print("Check the server logs for detailed error messages")