"""
Performance Monitor - Tracks system performance metrics and response times
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
from functools import wraps
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitors and tracks system performance metrics"""
    
    def __init__(self):
        self.metrics_file = "data/performance_metrics.json"
        self.current_requests = {}  # Track ongoing requests
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        
        # Initialize metrics file
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, "w") as f:
                json.dump([], f)
    
    def start_request(self, request_id: str, endpoint: str, query: str = "") -> None:
        """Start tracking a request"""
        self.current_requests[request_id] = {
            "endpoint": endpoint,
            "query": query[:100],  # Truncate long queries
            "start_time": time.time(),
            "stages": {}
        }
    
    def log_stage(self, request_id: str, stage: str, duration: float = None) -> None:
        """Log a stage completion time"""
        if request_id in self.current_requests:
            if duration is None:
                # Calculate duration from start time
                duration = time.time() - self.current_requests[request_id]["start_time"]
            
            self.current_requests[request_id]["stages"][stage] = duration
            logger.info(f"Request {request_id[:8]} - {stage}: {duration:.2f}s")
    
    def end_request(self, request_id: str, success: bool = True, 
                   source: str = "unknown", confidence: float = 0.0) -> None:
        """End tracking a request and save metrics"""
        if request_id not in self.current_requests:
            return
        
        request_data = self.current_requests[request_id]
        total_time = time.time() - request_data["start_time"]
        
        # Create performance entry
        performance_entry = {
            "request_id": request_id,
            "endpoint": request_data["endpoint"],
            "query": request_data["query"],
            "total_time": round(total_time, 3),
            "stages": {k: round(v, 3) for k, v in request_data["stages"].items()},
            "success": success,
            "source": source,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        self._save_metrics(performance_entry)
        
        # Clean up
        del self.current_requests[request_id]
        
        logger.info(f"Request {request_id[:8]} completed in {total_time:.2f}s - Source: {source}")
    
    def _save_metrics(self, entry: Dict[str, Any]) -> None:
        """Save performance metrics to file"""
        try:
            with open(self.metrics_file, "r") as f:
                metrics = json.load(f)
            
            metrics.append(entry)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(metrics) > 1000:
                metrics = metrics[-1000:]
            
            with open(self.metrics_file, "w") as f:
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")
    
    def get_performance_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance statistics for the last N hours"""
        try:
            with open(self.metrics_file, "r") as f:
                metrics = json.load(f)
            
            # Filter recent metrics
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = []
            
            for metric in metrics:
                try:
                    metric_time = datetime.fromisoformat(metric["timestamp"])
                    if metric_time >= cutoff_time:
                        recent_metrics.append(metric)
                except Exception:
                    continue
            
            if not recent_metrics:
                return {"message": f"No metrics found for the last {hours} hours"}
            
            # Calculate statistics
            total_requests = len(recent_metrics)
            successful_requests = len([m for m in recent_metrics if m["success"]])
            
            # Response times
            response_times = [m["total_time"] for m in recent_metrics]
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Success rate
            success_rate = (successful_requests / total_requests) * 100
            
            # Source distribution
            sources = {}
            for metric in recent_metrics:
                source = metric.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
            
            # Endpoint distribution
            endpoints = {}
            for metric in recent_metrics:
                endpoint = metric.get("endpoint", "unknown")
                endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
            
            # Performance by source
            source_performance = {}
            for source in sources.keys():
                source_metrics = [m for m in recent_metrics if m.get("source") == source]
                if source_metrics:
                    source_times = [m["total_time"] for m in source_metrics]
                    source_performance[source] = {
                        "count": len(source_metrics),
                        "avg_time": round(sum(source_times) / len(source_times), 3),
                        "min_time": round(min(source_times), 3),
                        "max_time": round(max(source_times), 3)
                    }
            
            # Cache hit analysis (if cache info is available)
            cache_hits = len([m for m in recent_metrics if "cache" in m.get("source", "").lower()])
            cache_hit_rate = (cache_hits / total_requests) * 100 if total_requests > 0 else 0
            
            return {
                "period_hours": hours,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": round(success_rate, 2),
                "response_times": {
                    "average": round(avg_response_time, 3),
                    "minimum": round(min_response_time, 3),
                    "maximum": round(max_response_time, 3)
                },
                "cache_hit_rate": round(cache_hit_rate, 2),
                "source_distribution": sources,
                "endpoint_distribution": endpoints,
                "performance_by_source": source_performance,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {"error": str(e)}
    
    def get_slow_queries(self, threshold: float = 5.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get queries that took longer than threshold seconds"""
        try:
            with open(self.metrics_file, "r") as f:
                metrics = json.load(f)
            
            # Filter slow queries
            slow_queries = [
                m for m in metrics 
                if m.get("total_time", 0) > threshold
            ]
            
            # Sort by response time (slowest first)
            slow_queries.sort(key=lambda x: x.get("total_time", 0), reverse=True)
            
            # Return limited results
            return slow_queries[:limit]
            
        except Exception as e:
            logger.error(f"Error getting slow queries: {e}")
            return []
    
    def clear_metrics(self) -> None:
        """Clear all performance metrics"""
        try:
            with open(self.metrics_file, "w") as f:
                json.dump([], f)
            logger.info("Cleared all performance metrics")
        except Exception as e:
            logger.error(f"Error clearing metrics: {e}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def track_performance(endpoint: str):
    """Decorator to track performance of async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate request ID
            request_id = f"{endpoint}_{int(time.time() * 1000)}"
            
            # Extract query if available
            query = ""
            if kwargs.get("math_query"):
                query = kwargs["math_query"].query
            elif len(args) > 1 and hasattr(args[1], 'query'):
                query = args[1].query
            
            # Start tracking
            performance_monitor.start_request(request_id, endpoint, query)
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Extract result info
                success = True
                source = "unknown"
                confidence = 0.0
                
                if hasattr(result, 'source'):
                    source = result.source
                if hasattr(result, 'confidence'):
                    confidence = result.confidence
                
                # End tracking
                performance_monitor.end_request(request_id, success, source, confidence)
                
                return result
                
            except Exception as e:
                # End tracking with error
                performance_monitor.end_request(request_id, False, "error", 0.0)
                raise
        
        return wrapper
    return decorator