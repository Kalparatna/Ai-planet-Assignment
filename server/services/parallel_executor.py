"""Parallel Executor - Handles asynchronous and parallel execution of tasks"""

import asyncio
import logging
from typing import Dict, Any, List, Callable, Awaitable, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParallelExecutor:
    """Service for executing tasks in parallel with timeouts and error handling"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    
    async def execute_parallel(
        self, 
        tasks: List[Callable[[], Awaitable[Any]]], 
        timeout: float = 10.0,
        return_exceptions: bool = False
    ) -> List[Any]:
        """Execute multiple async tasks in parallel with timeout"""
        task_coroutines = [task() for task in tasks]
        
        try:
            # Wait for tasks with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*task_coroutines, return_exceptions=return_exceptions),
                timeout=timeout
            )
            return results
        except asyncio.TimeoutError:
            logger.warning(f"Parallel execution timed out after {timeout} seconds")
            if return_exceptions:
                return [asyncio.TimeoutError(f"Task timed out after {timeout}s") for _ in tasks]
            raise
        except Exception as e:
            logger.error(f"Error in parallel execution: {e}")
            if return_exceptions:
                return [e for _ in tasks]
            raise
    
    async def execute_with_priority(
        self,
        tasks: List[Tuple[Callable[[], Awaitable[Any]], int]],  # (task, priority)
        timeout: float = 10.0,
        return_first_success: bool = False
    ) -> Union[List[Any], Any]:
        """Execute tasks in priority order, optionally returning first success"""
        # Sort tasks by priority (lower number = higher priority)
        sorted_tasks = sorted(tasks, key=lambda x: x[1])
        task_funcs = [task[0] for task in sorted_tasks]
        
        if return_first_success:
            for task_func in task_funcs:
                try:
                    result = await asyncio.wait_for(task_func(), timeout=timeout)
                    if result:  # Consider non-None/non-False as success
                        return result
                except (asyncio.TimeoutError, Exception) as e:
                    logger.warning(f"Task failed or timed out: {e}")
                    continue
            return None  # No successful result
        else:
            # Execute all tasks in parallel
            return await self.execute_parallel(task_funcs, timeout, return_exceptions=True)
    
    async def execute_with_fallback(
        self,
        primary_task: Callable[[], Awaitable[Any]],
        fallback_task: Callable[[], Awaitable[Any]],
        timeout: float = 10.0
    ) -> Any:
        """Execute primary task with fallback if it fails or times out"""
        try:
            # Try primary task first
            return await asyncio.wait_for(primary_task(), timeout=timeout)
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Primary task failed, using fallback: {e}")
            # Fall back to secondary task
            try:
                return await asyncio.wait_for(fallback_task(), timeout=timeout)
            except (asyncio.TimeoutError, Exception) as fallback_error:
                logger.error(f"Fallback task also failed: {fallback_error}")
                raise
    
    async def execute_search_pipeline(
        self,
        query: str,
        search_functions: List[Callable[[str], Awaitable[Dict[str, Any]]]],
        timeout: float = 10.0
    ) -> Dict[str, Any]:
        """Execute search pipeline with multiple search functions"""
        # Create tasks from search functions
        tasks = [lambda f=func: f(query) for func in search_functions]
        
        # Execute all search functions in parallel
        results = await self.execute_parallel(tasks, timeout, return_exceptions=True)
        
        # Process results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Search function {i} failed: {result}")
                continue
            
            if result and result.get("found", False):
                valid_results.append((result, result.get("confidence", 0.0)))
        
        # Return highest confidence result or None
        if valid_results:
            # Sort by confidence (descending)
            valid_results.sort(key=lambda x: x[1], reverse=True)
            return valid_results[0][0]
        
        return {"found": False}
    
    async def run_in_thread(self, func, *args, **kwargs) -> Any:
        """Run a blocking function in a thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.thread_pool,
            lambda: func(*args, **kwargs)
        )
    
    def close(self):
        """Close the thread pool"""
        self.thread_pool.shutdown()