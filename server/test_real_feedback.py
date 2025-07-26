#!/usr/bin/env python3
"""
Test script to verify HTML formatting is working correctly in the UI
"""

import requests
import json

def test_html_formatting():
    """Test that HTML formatting is properly handled"""
    
    print("🧪 Testing HTML Formatting for UI")
    print("=" * 60)
    
    # Test queries that typically produce HTML-heavy responses
    test_queries = [
        "Find the derivative of f(x) = x³ + 2x² - 4x + 7",
        "Solve the quadratic equation x² - 5x + 6 = 0",
        "Calculate the integral of x² dx",
        "Find the area of a circle with radius 5 cm"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = requests.post(
                "http://localhost:8000/math/solve",
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Response received successfully")
                print(f"   Source: {result.get('source')}")
                print(f"   Confidence: {result.get('confidence')}")
                
                solution = result.get('solution', '')
                
                # Check for HTML issues
                html_issues = []
                if '<sup>' in solution or '</sup>' in solution:
                    html_issues.append("Contains <sup> tags")
                if '<sub>' in solution or '</sub>' in solution:
                    html_issues.append("Contains <sub> tags")
                if '**' in solution and solution.count('**') % 2 != 0:
                    html_issues.append("Unmatched ** markdown")
                if 'SolutionProblem:' in solution.replace(' ', ''):
                    html_issues.append("Concatenated Problem/Solution")
                
                if html_issues:
                    print(f"   ⚠️  HTML Issues Found: {', '.join(html_issues)}")
                else:
                    print(f"   ✅ No HTML formatting issues detected")
                
                # Show formatted preview
                print(f"   📄 Solution Preview:")
                preview = solution[:200].replace('\n', ' ').strip()
                print(f"      {preview}...")
                
                # Check if solution is properly structured
                if '## Problem' in solution or '### Step' in solution:
                    print(f"   ✅ Solution is properly structured")
                else:
                    print(f"   ⚠️  Solution may need better structuring")
                
            else:
                print(f"❌ Request failed!")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server!")
            print("   Make sure your server is running: python main.py")
            return False
        except Exception as e:
            print(f"❌ Error testing query: {e}")
    
    return True

def test_specific_html_cases():
    """Test specific HTML formatting cases"""
    
    print("\n🔍 Testing Specific HTML Cases")
    print("=" * 60)
    
    # Test with a query that's known to produce HTML issues
    html_heavy_query = "Explain the power rule for derivatives with examples"
    
    try:
        response = requests.post(
            "http://localhost:8000/math/solve",
            json={"query": html_heavy_query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            solution = result.get('solution', '')
            
            print("📋 Raw Solution Analysis:")
            print(f"   Length: {len(solution)} characters")
            print(f"   Lines: {len(solution.split(chr(10)))}")
            
            # Check for common HTML issues
            checks = {
                "HTML Tags": '<' in solution and '>' in solution,
                "Superscript": '<sup>' in solution,
                "Subscript": '<sub>' in solution,
                "Bold Markdown": '**' in solution,
                "Problem/Solution Separation": 'Problem:' in solution and 'Solution:' in solution,
                "Step Structure": 'Step' in solution or '###' in solution,
                "Mathematical Symbols": any(symbol in solution for symbol in ['²', '³', 'π', '∞', '≈'])
            }
            
            print("\n🔍 Content Analysis:")
            for check, found in checks.items():
                status = "✅ Found" if found else "❌ Missing"
                print(f"   {check}: {status}")
            
            # Show the actual formatted solution
            print(f"\n📄 Formatted Solution (First 500 chars):")
            print("-" * 50)
            print(solution[:500])
            if len(solution) > 500:
                print("...")
            print("-" * 50)
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in specific HTML test: {e}")

def test_ui_ready_format():
    """Test if the response is ready for UI consumption"""
    
    print("\n🎨 Testing UI-Ready Format")
    print("=" * 60)
    
    try:
        response = requests.post(
            "http://localhost:8000/math/solve",
            json={"query": "Find the derivative of x² + 3x + 1"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if response has UI-friendly structure
            ui_checks = {
                "Has solution": 'solution' in result,
                "Has source": 'source' in result,
                "Has confidence": 'confidence' in result,
                "Solution is string": isinstance(result.get('solution'), str),
                "Solution not empty": bool(result.get('solution', '').strip()),
                "No HTML tags": not any(tag in result.get('solution', '') for tag in ['<sup>', '<sub>', '<b>', '<i>']),
                "Proper line breaks": '\n' in result.get('solution', ''),
                "Mathematical notation": any(symbol in result.get('solution', '') for symbol in ['²', '³', 'x', '='])
            }
            
            print("🎯 UI Readiness Checks:")
            all_passed = True
            for check, passed in ui_checks.items():
                status = "✅ Pass" if passed else "❌ Fail"
                print(f"   {check}: {status}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print(f"\n🎉 Response is UI-ready!")
            else:
                print(f"\n⚠️  Response needs formatting improvements")
            
            # Show the final formatted response
            print(f"\n📱 Final UI Response:")
            print(json.dumps(result, indent=2)[:800])
            if len(json.dumps(result, indent=2)) > 800:
                print("...")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in UI format test: {e}")

if __name__ == "__main__":
    print("🚀 Testing HTML Formatting for UI Display")
    print("=" * 80)
    
    # Run all tests
    test_html_formatting()
    test_specific_html_cases()
    test_ui_ready_format()
    
    print("\n" + "=" * 80)
    print("📋 Test Summary:")
    print("✅ If all tests pass, your UI should display properly formatted solutions")
    print("⚠️  If tests show issues, check the response_formatter.py implementation")
    print("🔧 The formatter should clean HTML tags and structure content for UI display")
    
    print("\n💡 Next Steps:")
    print("1. Check your UI to see if mathematical solutions display properly")
    print("2. Look for clean formatting without HTML tags")
    print("3. Verify that mathematical symbols render correctly")
    print("4. Test feedback submission with the improved formatting")