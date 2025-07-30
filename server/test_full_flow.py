#!/usr/bin/env python3
"""
Test Full Flow with Unique Queries
"""

import asyncio
from services.optimized_math_router import optimized_router

async def test_full_flow():
    print('🧪 Testing Full Flow with Unique Queries')
    print('=' * 50)
    
    # Test queries that definitely won't be cached
    test_queries = [
        'calculate the hyperbolic sine of 2.5 radians',
        'find the eigenvalues of a 3x3 matrix with elements [1,2,3;4,5,6;7,8,9]',
        'what is the Laplace transform of t^3 * e^(-2t)',
        'solve the differential equation dy/dx = x*y with initial condition y(0)=1'
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f'\n🧮 Test {i}: {query[:50]}...')
        
        result = await optimized_router.route_query(query)
        
        print(f'✅ Source: {result.get("source", "Unknown")}')
        print(f'✅ Response Time: {result.get("response_time", 0):.3f}s')
        print(f'✅ Found: {result.get("found", False)}')
        print(f'✅ Solution Length: {len(result.get("solution", ""))} chars')
        
        # Check which phase was used
        source = result.get('source', '')
        if 'Pattern' in source:
            print('✅ Phase: Pattern Matching')
        elif 'JEE Bench' in source or 'MongoDB' in source:
            print('✅ Phase: Knowledge Base (Cached)')
        elif 'Web Search' in source:
            print('✅ Phase: Web Search')
        elif 'AI Generated' in source:
            print('✅ Phase: AI Generation')
        else:
            print(f'⚠️ Phase: Unknown ({source})')

if __name__ == "__main__":
    asyncio.run(test_full_flow())