import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, TEXT
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self):
        # Local MongoDB connection
        self.client = None
        self.db = None
        self.collections = {}
        self.connection_string = "mongodb://localhost:27017"
        self.database_name = "math_routing_agent"
        
    async def connect(self):
        """Connect to local MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            
            # Initialize collections
            self.collections = {
                'math_solutions': self.db.math_solutions,
                'web_search_cache': self.db.web_search_cache,
                'jee_bench_data': self.db.jee_bench_data,
                'query_patterns': self.db.query_patterns,
                'performance_logs': self.db.performance_logs
            }
            
            # Create indexes for fast queries
            await self._create_indexes()
            
            logger.info("Connected to MongoDB successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def _create_indexes(self):
        """Create indexes for fast queries"""
        try:
            # Math solutions indexes
            await self.collections['math_solutions'].create_index([("query", TEXT)])
            await self.collections['math_solutions'].create_index("category")
            await self.collections['math_solutions'].create_index("difficulty")
            
            # Web search cache indexes
            await self.collections['web_search_cache'].create_index([("query", TEXT)])
            await self.collections['web_search_cache'].create_index("created_at")
            
            # JEE bench data indexes
            await self.collections['jee_bench_data'].create_index([("problem", TEXT)])
            await self.collections['jee_bench_data'].create_index("subject")
            
            # Query patterns indexes
            await self.collections['query_patterns'].create_index("pattern")
            await self.collections['query_patterns'].create_index("response_time")
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    # MATH SOLUTIONS OPERATIONS
    async def get_math_solution(self, query: str) -> Optional[Dict[str, Any]]:
        """Get math solution from MongoDB with STRICT query matching - NO RANDOM ANSWERS"""
        try:
            query_lower = query.lower().strip()
            
            # STRICT: Only exact matches or very high similarity
            # First try exact match
            exact_result = await self.collections['math_solutions'].find_one(
                {"query": query_lower},
                {"solution": 1, "confidence": 1, "category": 1, "_id": 0}
            )
            
            if exact_result:
                logger.info(f"✅ EXACT match found for: {query}")
                return {
                    "found": True,
                    "solution": exact_result["solution"],
                    "confidence": exact_result.get("confidence", 0.9),
                    "source": "Knowledge Base"
                }
            
            # Check for basic math patterns only (no random text search)
            basic_patterns = {
                "area of circle": "A = πr² where r is the radius",
                "area of rectangle": "A = length × width", 
                "pythagorean theorem": "a² + b² = c² where c is the hypotenuse",
                "quadratic formula": "x = (-b ± √(b²-4ac)) / 2a",
                "slope formula": "m = (y₂-y₁)/(x₂-x₁)"
            }
            
            for pattern, solution in basic_patterns.items():
                if pattern in query_lower:
                    logger.info(f"✅ Basic pattern match found: {pattern}")
                    return {
                        "found": True,
                        "solution": f"**Formula:** {solution}\n\n**This is a fundamental mathematical concept.**",
                        "confidence": 0.95,
                        "source": "Knowledge Base"
                    }
            
            # NO TEXT SEARCH - prevents random answers
            logger.info(f"❌ No exact match found in knowledge base for: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting math solution: {e}")
            return None
    
    async def store_math_solution(self, query: str, solution: str, category: str = "general", confidence: float = 0.8):
        """Store math solution in MongoDB"""
        try:
            document = {
                "query": query.lower().strip(),
                "solution": solution,
                "category": category,
                "confidence": confidence,
                "created_at": datetime.now(),
                "usage_count": 1
            }
            
            # Upsert to avoid duplicates - fix usage_count conflict
            await self.collections['math_solutions'].update_one(
                {"query": query.lower().strip()},
                {
                    "$set": {
                        "query": document["query"],
                        "solution": document["solution"],
                        "category": document["category"],
                        "confidence": document["confidence"],
                        "created_at": document["created_at"]
                    },
                    "$inc": {"usage_count": 1}
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error storing math solution: {e}")
    
    # WEB SEARCH CACHE OPERATIONS
    async def get_web_search_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached web search result - ULTRA FAST"""
        try:
            result = await self.collections['web_search_cache'].find_one(
                {"query": query.lower().strip()},
                {"solution": 1, "references": 1, "confidence": 1, "_id": 0}
            )
            
            if result:
                return {
                    "found": True,
                    "solution": result["solution"],
                    "confidence": result.get("confidence", 0.8),
                    "references": result.get("references", []),
                    "source": "Web Cache"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting web search cache: {e}")
            return None
    
    async def store_web_search_cache(self, query: str, solution: str, references: List[str], confidence: float = 0.8):
        """Store web search result in cache"""
        try:
            document = {
                "query": query.lower().strip(),
                "solution": solution,
                "references": references,
                "confidence": confidence,
                "created_at": datetime.now()
            }
            
            await self.collections['web_search_cache'].insert_one(document)
            
        except Exception as e:
            logger.error(f"Error storing web search cache: {e}")
    
    # JEE BENCH DATA OPERATIONS REMOVED PER USER REQUIREMENTS
    # User specifically requested NO JEE bench data - only sample data, web search, and AI generation
    
    async def store_jee_data(self, problems: List[Dict[str, Any]]):
        """Store JEE bench data in MongoDB"""
        try:
            if problems:
                await self.collections['jee_bench_data'].insert_many(problems)
                logger.info(f"Stored {len(problems)} JEE problems in MongoDB")
                
        except Exception as e:
            logger.error(f"Error storing JEE data: {e}")
    
    # QUERY PATTERNS OPERATIONS
    async def get_query_pattern(self, query: str) -> Optional[Dict[str, Any]]:
        """Get query pattern for fast routing"""
        try:
            # Simple pattern matching for common queries
            patterns = [
                ("area", "geometry"),
                ("volume", "geometry"),
                ("derivative", "calculus"),
                ("integral", "calculus"),
                ("solve", "algebra"),
                ("factor", "algebra"),
                ("graph", "algebra"),
                ("limit", "calculus")
            ]
            
            query_lower = query.lower()
            for pattern, category in patterns:
                if pattern in query_lower:
                    return {
                        "category": category,
                        "confidence": 0.8,
                        "fast_route": True
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting query pattern: {e}")
            return None
    
    # PERFORMANCE LOGGING
    async def log_performance(self, query: str, response_time: float, source: str, success: bool):
        """Log performance metrics"""
        try:
            document = {
                "query": query,
                "response_time": response_time,
                "source": source,
                "success": success,
                "timestamp": datetime.now()
            }
            
            await self.collections['performance_logs'].insert_one(document)
            
        except Exception as e:
            logger.error(f"Error logging performance: {e}")
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$source",
                        "avg_response_time": {"$avg": "$response_time"},
                        "total_queries": {"$sum": 1},
                        "success_rate": {"$avg": {"$cond": ["$success", 1, 0]}}
                    }
                }
            ]
            
            stats = []
            async for stat in self.collections['performance_logs'].aggregate(pipeline):
                stats.append(stat)
            
            return {"performance_stats": stats}
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {"performance_stats": []}
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global MongoDB service instance
mongodb_service = MongoDBService()