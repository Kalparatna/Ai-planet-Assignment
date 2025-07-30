"""
Connection Manager - Handles connection pooling and timeouts for all external APIs
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional
import os

# Configure logging
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages HTTP connections with pooling and timeouts"""
    
    def __init__(self):
        self.session = None
        self.timeout_config = aiohttp.ClientTimeout(
            total=30,      # Total timeout for the entire request
            connect=10,    # Timeout for establishing connection
            sock_read=20   # Timeout for reading response
        )
        
        # Connection pool settings
        self.connector_config = {
            'limit': 100,           # Total connection pool size
            'limit_per_host': 30,   # Max connections per host
            'ttl_dns_cache': 300,   # DNS cache TTL (5 minutes)
            'use_dns_cache': True,
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(**self.connector_config)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout_config,
                headers={
                    'User-Agent': 'Math-Routing-Agent/1.0',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                }
            )
            logger.info("Created new HTTP session with connection pooling")
        
        return self.session
    
    async def close_session(self):
        """Close HTTP session and cleanup connections"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Closed HTTP session")
    
    async def post_json(self, url: str, data: Dict[str, Any], 
                       headers: Optional[Dict[str, str]] = None,
                       timeout: Optional[int] = None) -> Dict[str, Any]:
        """Make POST request with JSON data"""
        session = await self.get_session()
        
        # Override timeout if specified
        request_timeout = self.timeout_config
        if timeout:
            request_timeout = aiohttp.ClientTimeout(total=timeout)
        
        try:
            async with session.post(
                url, 
                json=data, 
                headers=headers or {},
                timeout=request_timeout
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout error for POST {url}")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for POST {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for POST {url}: {e}")
            raise
    
    async def get_json(self, url: str, params: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None,
                      timeout: Optional[int] = None) -> Dict[str, Any]:
        """Make GET request and return JSON response"""
        session = await self.get_session()
        
        # Override timeout if specified
        request_timeout = self.timeout_config
        if timeout:
            request_timeout = aiohttp.ClientTimeout(total=timeout)
        
        try:
            async with session.get(
                url,
                params=params,
                headers=headers or {},
                timeout=request_timeout
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout error for GET {url}")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for GET {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for GET {url}: {e}")
            raise
    
    async def get_text(self, url: str, params: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None,
                      timeout: Optional[int] = None) -> str:
        """Make GET request and return text response"""
        session = await self.get_session()
        
        # Override timeout if specified
        request_timeout = self.timeout_config
        if timeout:
            request_timeout = aiohttp.ClientTimeout(total=timeout)
        
        try:
            async with session.get(
                url,
                params=params,
                headers=headers or {},
                timeout=request_timeout
            ) as response:
                response.raise_for_status()
                return await response.text()
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout error for GET {url}")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error for GET {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for GET {url}: {e}")
            raise

# Global connection manager instance
connection_manager = ConnectionManager()

# Cleanup function for graceful shutdown
async def cleanup_connections():
    """Cleanup connections on shutdown"""
    await connection_manager.close_session()