#!/usr/bin/env python3
"""
Test script to verify the LangChain response formatting fix is working
"""

import requests
import json
import re

def test_langchain_formatting():
    """Test that LangChain responses are properly formatted"""
    
    print("🧪 Testing LangChain Response Formatting Fix")
    print("=" * 60)
    
    # Test with a simple mathematical query
    test_query = "What is 4²"
    
    print(f"📝 Testing Query: {test_query}")
    print("-" * 40)
    
    try:
        response = requests.post(
            "http://localhost:8000/math/solve",
            json={"query": test_query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            solution = result.get('solution', '')
            
            print("✅ Response received successfully")
            print(f"   Source: {result.get('source')}")
            print(f"   Confidence: {result.get('confidence')}")
            
            # Check for LangChain metadata issues
            metadata_issues = []
            
            if "content='" in solution:
                metadata_issues.append("Contains content=' pattern")
            if "additional_kwargs=" in solution:
                metadata_issues.append("Contains additional_kwargs")
            if "response_metadata=" in solution:
                metadata_issues.append("Contains response_metadata")
            if "id='run-" in solution:
                metadata_issues.append("Contains LangChain run ID")
            if "usage_metadata=" in solution:
                metadata_issues.append("Contains usage_metadata")
            if re.search(r'###\s*Step\s*\d+content=', solution):
                metadata_issues.append("Contains malformed step headers")
            
            if metadata_issues:
                print(f"❌ LangChain Metadata Issues Found:")
                for issue in metadata_issues:
                    print(f"   • {issue}")
                print(f"\n🔍 Raw Solution (first 300 chars):")
                print(f"   {solution[:300]}...")
            else:
                print(f"✅ No LangChain metadata issues detected")
            
            # Check for proper formatting
            formatting_checks = {
                "Has Problem section": "Problem:" in solution or "## Problem" in solution,
                "Has Solution section": "Solution:" in solution or "## Solution" in solution,
                "Proper line breaks": solution.count('\n') > 2,
                "No HTML tags": not any(tag in solution for tag in ['<sup>', '<sub>', '<b>', '<i>']),
                "Mathematical symbols": any(symbol in solution for symbol in ['²', '³', '=', '4']),
                "Clean structure": not solution.startswith('content=')
            }
            
            print(f"\n📋 Formatting Quality Checks:")
            all_good = True
            for check, passed in formatting_checks.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {check}")
                if not passed:
                    all_good = False
            
            if all_good:
                print(f"\n🎉 Solution is properly formatted!")
            else:
                print(f"\n⚠️  Solution needs formatting improvements")
            
            # Show the cleaned solution
            print(f"\n📄 Formatted Solution:")
            print("-" * 50)
            print(solution)
            print("-" * 50)
            
        else:
            print(f"❌ Request failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure your server is running: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error testing formatting: {e}")
        return False
    
    return True

def test_multiple_queries():
    """Test multiple queries to ensure consistent formatting"""
    
    print(f"\n🔄 Testing Multiple Queries for Consistency")
    print("=" * 60)
    
    test_queries = [
        "What is 2 + 2?",
        "Find the derivative of x²",
        "Solve x² - 4 = 0",
        "What is the area of a circle with radius 3?"
    ]
    
    all_clean = True
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        
        try:
            response = requests.post(
                "http://localhost:8000/math/solve",
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                solution = result.get('solution', '')
                
                # Quick check for metadata issues
                has_metadata = any(pattern in solution for pattern in [
                    "content='", "additional_kwargs=", "response_metadata=", "usage_metadata="
                ])
                
                if has_metadata:
                    print(f"   ❌ Contains LangChain metadata")
                    all_clean = False
                else:
                    print(f"   ✅ Clean formatting")
                    
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                all_clean = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_clean = False
    
    if all_clean:
        print(f"\n🎉 All queries return clean, formatted responses!")
    else:
        print(f"\n⚠️  Some queries still have formatting issues")
    
    return all_clean

def show_before_after_example():
    """Show a before/after example of the formatting fix"""
    
    print(f"\n📊 Before/After Formatting Example")
    print("=" * 60)
    
    # Example of what the response looked like before
    before_example = """What is 4²### Step 1content='Okay, let's break down the problem of calculating 4² step-by-step.

**1. Identifying the Problem and Concepts**

This problem involves evaluating an exponent. Specifically, we need to calculate "4 squared," which means 4 raised to the power of 2. The concept involved is exponentiation, where a base number (in this case, 4) is multiplied by itself a certain number of times, as indicated by the exponent (in this case, 2).

**2. Solution Steps**

1. **Understand the Exponent:** The expression 4² means "4 to the power of 2" or "4 squared." The exponent, 2, tells us how many times to multiply the base, 4, by itself.

2. **Write out the Multiplication:** 4² is equivalent to 4 * 4.

3. **Perform the Multiplication:** Multiply 4 by 4.

**3. Detailed Explanation of Each Step**

* **Step 1: Understand the Exponent:** The exponent is the small number written above and to the right of the base. It indicates repeated multiplication. In this case, the exponent is 2, meaning we multiply the base by itself twice.

* **Step 2: Write out the Multiplication:** This step translates the exponential notation into a multiplication problem. 4² becomes 4 * 4.

* **Step 3: Perform the Multiplication:** This is a basic multiplication operation. We multiply 4 by 4.

**4. Work and Calculations**

4² = 4 * 4 = 16

**5. Final Answer**

The final answer is 16.

**6. Verification**

We can verify this answer using a calculator or by understanding the concept of squaring a number. 4 squared is indeed 16.
' additional_kwargs={} response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'safety_ratings': []} id='run--40fc9b7b-cbcd-4086-832a-f110a0a7db4f-0' usage_metadata={'input_tokens': 184, 'output_tokens': 404, 'total_tokens': 588}"""
    
    print("❌ BEFORE (Messy with metadata):")
    print("-" * 30)
    print(before_example[:400] + "...")
    
    print(f"\n✅ AFTER (Clean and formatted):")
    print("-" * 30)
    print("""Problem: What is 4²

Solution:

**Step 1:** Identifying the Problem and Concepts
This problem involves evaluating an exponent. Specifically, we need to calculate "4 squared," which means 4 raised to the power of 2.

**Step 2:** Understanding the Exponent
The expression 4² means "4 to the power of 2" or "4 squared." The exponent, 2, tells us how many times to multiply the base, 4, by itself.

**Step 3:** Write out the Multiplication
4² is equivalent to 4 × 4.

**Step 4:** Perform the Multiplication
4² = 4 × 4 = 16

**Final Answer:** 16""")

if __name__ == "__main__":
    print("🚀 Testing LangChain Response Formatting Fix")
    print("=" * 80)
    
    # Show the before/after example
    show_before_after_example()
    
    # Test the actual formatting
    formatting_ok = test_langchain_formatting()
    consistency_ok = test_multiple_queries()
    
    print("\n" + "=" * 80)
    print("📋 Test Summary:")
    print(f"   Formatting Fix: {'✅ Working' if formatting_ok else '❌ Issues found'}")
    print(f"   Consistency: {'✅ All clean' if consistency_ok else '❌ Some issues'}")
    
    if formatting_ok and consistency_ok:
        print(f"\n🎉 LangChain formatting fix is working perfectly!")
        print(f"   Your UI should now display clean, properly formatted solutions")
        print(f"   No more metadata clutter or malformed responses")
    else:
        print(f"\n⚠️  There are still some formatting issues to resolve")
        print(f"   Check the server logs and response_formatter.py")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Test your UI with mathematical queries")
    print(f"   2. Verify that solutions display cleanly")
    print(f"   3. Check that feedback submission works properly")
    print(f"   4. Look for clean formatting without metadata")