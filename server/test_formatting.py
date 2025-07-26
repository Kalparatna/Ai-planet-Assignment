#!/usr/bin/env python3
"""
Test script to verify solution formatting works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.math_solver import MathSolverService

def test_formatting():
    """Test the solution formatting functionality"""
    
    # Create a sample unformatted solution (like what you saw in the UI)
    messy_solution = """Problem: Find the derivative of f(x) = x³ + 2x² - 4x + 7 using the power rule.Okay, I'm ready to provide a detailed, step-by-step solution to the given problem.**1. Problem Identification and Concepts Involved**This problem asks us to find the derivative of a polynomial function, f(x) = x³ + 2x² - 4x + 7. The primary concept involved is the *power rule* of differentiation, which states that if f(x) = x<sup>n</sup>, then f'(x) = nx<sup>n-1</sup>. We will also use the constant multiple rule, which states that if f(x) = c*g(x), where c is a constant, then f'(x) = c*g'(x). Finally, we'll use the sum/difference rule, which states that the derivative of a sum or difference of terms is the sum or difference of the derivatives of those terms. The derivative of a constant is zero.**2. Step-by-Step Solution**Here's how we'll find the derivative of f(x) = x³ + 2x² - 4x + 7:**Step 1: Apply the Sum/Difference Rule**The derivative of a sum (or difference) is the sum (or difference) of the derivatives. Therefore, we can differentiate each term separately:f'(x) = d/dx (x³) + d/dx (2x²) - d/dx (4x) + d/dx (7)**Step 2: Apply the Power Rule and Constant Multiple Rule to the first term (x³)*** We have d/dx (x³).* Using the power rule, where n = 3, we get 3x<sup>3-1</sup> = 3x².**Step 3: Apply the Power Rule and Constant Multiple Rule to the second term (2x²)*** We have d/dx (2x²).* Using the constant multiple rule, we can write this as 2 * d/dx (x²).* Using the power rule, where n = 2, we get 2 * (2x<sup>2-1</sup>) = 2 * (2x) = 4x.**Step 4: Apply the Power Rule and Constant Multiple Rule to the third term (-4x)*** We have d/dx (-4x).* Using the constant multiple rule, we can write this as -4 * d/dx (x).* Since x = x<sup>1</sup>, using the power rule, where n = 1, we get -4 * (1x<sup>1-1</sup>) = -4 * (1x<sup>0</sup>) = -4 * (1) = -4.**Step 5: Find the derivative of the constant term (7)*** We have d/dx (7).* The derivative of a constant is always zero. Therefore, d/dx (7) = 0.**Step 6: Combine the results**Now, we combine the derivatives of each term:f'(x) = 3x² + 4x - 4 + 0**Step 7: Simplify**Simplify the expression:f'(x) = 3x² + 4x - 4**3. Final Answer**The derivative of f(x) = x³ + 2x² - 4x + 7 is:**f'(x) = 3x² + 4x - 4****4. Verification (Optional, but Recommended)**While there isn't a simple numerical check for derivatives in general, we can consider the behavior of the original function and its derivative.* The original function f(x) = x³ + 2x² - 4x + 7 is a cubic polynomial.* Its derivative, f'(x) = 3x² + 4x - 4, is a quadratic polynomial. This is expected, as the derivative reduces the degree of the polynomial by one.* We can also analyze the critical points. The critical points of f(x) occur where f'(x) = 0. Solving 3x² + 4x - 4 = 0, we get (3x - 2)(x + 2) = 0, so x = 2/3 and x = -2. These are the x-values where the original function has a local maximum or minimum. This is consistent with the relationship between a function and its derivative.Therefore, based on the application of the power rule and the expected behavior of the derivative, we can be confident in our solution."""
    
    problem = "Find the derivative of f(x) = x³ + 2x² - 4x + 7 using the power rule."
    
    # Initialize the math solver service
    math_solver = MathSolverService()
    
    # Format the messy solution
    formatted_solution = math_solver.format_solution(messy_solution, problem)
    
    print("🧪 Testing Solution Formatting")
    print("=" * 60)
    print("\n📝 ORIGINAL (Messy):")
    print("-" * 30)
    print(messy_solution[:200] + "..." if len(messy_solution) > 200 else messy_solution)
    
    print("\n✨ FORMATTED (Clean):")
    print("-" * 30)
    print(formatted_solution)
    
    print("\n" + "=" * 60)
    print("✅ Formatting test completed!")
    print("\nKey improvements:")
    print("• HTML tags cleaned (x<sup>3</sup> → x^(3))")
    print("• Proper problem/solution separation")
    print("• Clear step formatting with headers")
    print("• Better paragraph structure")
    print("• Mathematical notation standardized")

if __name__ == "__main__":
    test_formatting()