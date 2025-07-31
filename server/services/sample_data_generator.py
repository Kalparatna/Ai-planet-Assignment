"""
Sample Data Generator - Creates sample mathematical problems for the knowledge base
"""

import json
import logging

logger = logging.getLogger(__name__)

class SampleDataGenerator:
    """Generates sample mathematical problems and solutions"""
    
    def create_sample_math_data(self, file_path: str):
        """Create sample math problems and solutions for the knowledge base"""
        sample_data = [
            {
                "id": "algebra-1",
                "problem": "Solve the quadratic equation: x^2 - 5x + 6 = 0",
                "solution": "To solve the quadratic equation x^2 - 5x + 6 = 0, we can use the factoring method.\n\nStep 1: Identify the coefficients.\na = 1, b = -5, c = 6\n\nStep 2: Find two numbers that multiply to give 'c' (which is 6) and add up to 'b' (which is -5).\nThe numbers -2 and -3 multiply to give 6 and add up to -5.\n\nStep 3: Rewrite the middle term using these numbers.\nx^2 - 5x + 6 = x^2 - 2x - 3x + 6 = x(x - 2) - 3(x - 2) = (x - 2)(x - 3)\n\nStep 4: Set each factor equal to zero and solve.\nx - 2 = 0 → x = 2\nx - 3 = 0 → x = 3\n\nTherefore, the solutions to the equation x^2 - 5x + 6 = 0 are x = 2 and x = 3.",
                "category": "Algebra",
                "difficulty": "Easy",
                "tags": ["quadratic equation", "factoring", "algebra"]
            },
            {
                "id": "calculus-1",
                "problem": "Find the derivative of f(x) = x^3 - 4x^2 + 7x - 9",
                "solution": "To find the derivative of f(x) = x^3 - 4x^2 + 7x - 9, we'll use the power rule and the sum rule of differentiation.\n\nThe power rule states that if f(x) = x^n, then f'(x) = n·x^(n-1).\nThe sum rule states that the derivative of a sum is the sum of the derivatives.\n\nLet's differentiate each term:\n\nFor x^3: f'(x) = 3x^2\nFor -4x^2: f'(x) = -4 · 2x = -8x\nFor 7x: f'(x) = 7\nFor -9: f'(x) = 0 (the derivative of a constant is zero)\n\nCombining all terms:\nf'(x) = 3x^2 - 8x + 7\n\nTherefore, the derivative of f(x) = x^3 - 4x^2 + 7x - 9 is f'(x) = 3x^2 - 8x + 7.",
                "category": "Calculus",
                "difficulty": "Medium",
                "tags": ["calculus", "derivative", "polynomial"]
            },
            {
                "id": "geometry-1",
                "problem": "Find the area of a circle with radius 5 cm.",
                "solution": "To find the area of a circle, we use the formula: A = πr², where r is the radius.\n\nGiven information:\n- Radius (r) = 5 cm\n\nStep 1: Substitute the radius into the formula.\nA = π × 5²\nA = π × 25\n\nStep 2: Calculate the result.\nA = 25π cm²\n\nIf we use π ≈ 3.14159, then:\nA ≈ 25 × 3.14159\nA ≈ 78.54 cm²\n\nTherefore, the area of the circle with radius 5 cm is 25π cm² or approximately 78.54 cm².",
                "category": "Geometry",
                "difficulty": "Easy",
                "tags": ["geometry", "circle", "area"]
            },
            {
                "id": "trigonometry-1",
                "problem": "Prove the identity: sin²θ + cos²θ = 1",
                "solution": "To prove the identity sin²θ + cos²θ = 1, we'll use the definitions of sine and cosine in terms of a right triangle.\n\nIn a right triangle with hypotenuse of length 1 (unit circle):\n- sin θ is the length of the opposite side\n- cos θ is the length of the adjacent side\n\nBy the Pythagorean theorem, in a right triangle:\n(opposite)² + (adjacent)² = (hypotenuse)²\n\nSubstituting our definitions:\n(sin θ)² + (cos θ)² = 1²\nsin²θ + cos²θ = 1\n\nThis proves the identity sin²θ + cos²θ = 1, which is one of the fundamental Pythagorean identities in trigonometry.",
                "category": "Trigonometry",
                "difficulty": "Medium",
                "tags": ["trigonometry", "identity", "pythagorean identity"]
            },
            {
                "id": "statistics-1",
                "problem": "Calculate the mean, median, and mode of the following data set: 4, 7, 2, 8, 4, 9, 4, 6, 3",
                "solution": "Let's calculate the mean, median, and mode for the data set: 4, 7, 2, 8, 4, 9, 4, 6, 3\n\nStep 1: Calculate the mean (average).\nMean = (sum of all values) ÷ (number of values)\nMean = (4 + 7 + 2 + 8 + 4 + 9 + 4 + 6 + 3) ÷ 9\nMean = 47 ÷ 9\nMean ≈ 5.22\n\nStep 2: Calculate the median (middle value when arranged in order).\nFirst, arrange the data in ascending order: 2, 3, 4, 4, 4, 6, 7, 8, 9\nSince there are 9 values (odd number), the median is the 5th value.\nMedian = 4\n\nStep 3: Calculate the mode (most frequently occurring value).\nCounting the frequency of each value:\n2 appears 1 time\n3 appears 1 time\n4 appears 3 times\n6 appears 1 time\n7 appears 1 time\n8 appears 1 time\n9 appears 1 time\n\nThe value 4 appears most frequently (3 times), so:\nMode = 4\n\nTherefore:\n- Mean ≈ 5.22\n- Median = 4\n- Mode = 4",
                "category": "Statistics",
                "difficulty": "Easy",
                "tags": ["statistics", "mean", "median", "mode"]
            }
        ]
        
        # Save sample data
        with open(file_path, "w") as f:
            json.dump(sample_data, f, indent=2)
        
        logger.info("Created sample math data")
        return sample_data