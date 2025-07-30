#!/usr/bin/env python3
"""
Test Script to Verify Math Routing Agent Flow
Tests: Knowledge Base → Web Search → AI Generation
"""

import asyncio
import time
from services.optimized_math_router import optimized_router
from services.mongodb_service import mongodb_service

async def test_routing_flow():
    """Test the complete routing flow"""
    print("🧪 Testing Math Routing Agent Flow")
    print("=" * 50)
    
    # Connect to MongoDB
    await mongodb_service.connect()
    
    # Test cases
    test_cases = [
        {
            "name": "Simple Arithmetic (Should use Pattern Matching)",
            "query": "2 + 2",
            "expected_source": "Arithmetic Pattern"
        },
        {
            "name": "Common Formula (Should use Pattern Matching)",
            "query": "area of circle",
            "expected_source": "Formula Pattern"
        },
        {
            "name": "JEE Bench Problem (Should find in Knowledge Base)",
            "query": "solve quadratic equation x^2 + 5x + 6 = 0",
            "expected_source": "JEE Bench Dataset"
        },
        {
            "name": "Unknown Problem (Should go to Web Search then AI)",
            "query": "how to calculate the volume of an irregular dodecahedron",
            "expected_source": "Web Search or AI Generated"
        },
        {
            "name": "Word Problem (Should use Pattern Matching)",
            "query": "If 12-inch decorative garden bricks cost $2.32 each, and you want to lay two rows of bricks around a rectangular flower bed that measures 6 yards by 1 yard, how much will the bricks cost in total?",
            "expected_source": "Word Problem Pattern"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧮 Test {i}: {test_case['name']}")
        print(f"Query: {test_case['query'][:80]}...")
        
        start_time = time.time()
        
        try:
            result = await optimized_router.route_query(test_case['query'])
            response_time = time.time() - start_time
            
            # Extract key information
            found = result.get("found", False)
            source = result.get("source", "Unknown")
            solution = result.get("solution", "")
            confidence = result.get("confidence", 0)
            
            print(f"✅ Found: {found}")
            print(f"✅ Source: {source}")
            print(f"✅ Response Time: {response_time:.3f}s")
            print(f"✅ Confidence: {confidence}")
            print(f"✅ Solution Length: {len(solution)} characters")
            print(f"✅ Solution Preview: {solution[:150]}...")
            
            # Check if flow is correct
            flow_correct = True
            if test_case["expected_source"] in source:
                print(f"✅ Flow Correct: Expected {test_case['expected_source']}, Got {source}")
            else:
                print(f"⚠️ Flow Issue: Expected {test_case['expected_source']}, Got {source}")
                flow_correct = False
            
            results.append({
                "test_name": test_case["name"],
                "query": test_case["query"],
                "found": found,
                "source": source,
                "response_time": response_time,
                "confidence": confidence,
                "solution_length": len(solution),
                "flow_correct": flow_correct,
                "expected_source": test_case["expected_source"]
            })
            
        except Exception as e:
            print(f"❌ Test Failed: {e}")
            results.append({
                "test_name": test_case["name"],
                "query": test_case["query"],
                "error": str(e),
                "found": False,
                "flow_correct": False
            })
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get("found", False))
    correct_flow_tests = sum(1 for r in results if r.get("flow_correct", False))
    avg_response_time = sum(r.get("response_time", 0) for r in results) / total_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful Tests: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"Correct Flow Tests: {correct_flow_tests}/{total_tests} ({correct_flow_tests/total_tests*100:.1f}%)")
    print(f"Average Response Time: {avg_response_time:.3f}s")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS")
    print("-" * 50)
    for result in results:
        print(f"Test: {result['test_name']}")
        print(f"  Source: {result.get('source', 'Error')}")
        print(f"  Time: {result.get('response_time', 0):.3f}s")
        print(f"  Flow: {'✅ Correct' if result.get('flow_correct', False) else '❌ Incorrect'}")
        if 'error' in result:
            print(f"  Error: {result['error']}")
        print()
    
    # Recommendations
    print("🎯 RECOMMENDATIONS")
    print("-" * 30)
    
    if correct_flow_tests < total_tests:
        print("⚠️ Some tests didn't follow expected flow - check routing logic")
    
    if avg_response_time > 8.0:
        print("⚠️ Average response time exceeds 8-second target")
    elif avg_response_time < 3.0:
        print("✅ Excellent response time performance")
    
    if successful_tests < total_tests:
        print("⚠️ Some tests failed - check error handling")
    else:
        print("✅ All tests successful")
    
    return results

async def test_specific_issues():
    """Test specific issues mentioned"""
    print("\n🔍 TESTING SPECIFIC ISSUES")
    print("=" * 50)
    
    # Test 1: JEE Bench data quality
    print("\n1. Testing JEE Bench Data Quality...")
    jee_query = "solve x^2 + 2x + 1 = 0"
    result = await optimized_router.route_query(jee_query)
    
    print(f"Query: {jee_query}")
    print(f"Source: {result.get('source', 'Unknown')}")
    print(f"Solution: {result.get('solution', '')[:200]}...")
    
    if "JEE Bench" in result.get('source', ''):
        print("✅ JEE Bench data is being used")
    else:
        print("⚠️ JEE Bench data not found - may need to populate database")
    
    # Test 2: Web search functionality
    print("\n2. Testing Web Search Functionality...")
    web_query = "how to find the derivative of sin(x) cos(x)"
    result = await optimized_router.route_query(web_query)
    
    print(f"Query: {web_query}")
    print(f"Source: {result.get('source', 'Unknown')}")
    print(f"Solution: {result.get('solution', '')[:200]}...")
    
    if "Web Search" in result.get('source', ''):
        print("✅ Web search is working")
    elif "AI Generated" in result.get('source', ''):
        print("⚠️ Web search failed, fell back to AI generation")
    else:
        print("❌ Neither web search nor AI generation worked")
    
    # Test 3: Flow sequence
    print("\n3. Testing Flow Sequence...")
    unknown_query = "calculate the hyperbolic tangent of pi/4"
    
    print(f"Query: {unknown_query}")
    print("Expected flow: Knowledge Base → Web Search → AI Generation")
    
    result = await optimized_router.route_query(unknown_query)
    actual_source = result.get('source', 'Unknown')
    
    print(f"Actual source: {actual_source}")
    
    if actual_source in ["MongoDB", "Pattern", "JEE Bench", "Knowledge Base"]:
        print("✅ Found in Knowledge Base (Phase 1)")
    elif actual_source == "Web Search":
        print("✅ Found via Web Search (Phase 2)")
    elif "AI Generated" in actual_source:
        print("✅ Generated by AI (Phase 3)")
    else:
        print("❌ Unexpected source - flow may be broken")

if __name__ == "__main__":
    async def main():
        await test_routing_flow()
        await test_specific_issues()
    
    asyncio.run(main())