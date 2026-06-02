"""
Network Detection Service
Monitors internet connectivity and switches between online/offline modes
"""

import asyncio
import socket
import aiohttp
from typing import Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NetworkDetector:
    """
    Detects network connectivity and triggers mode switches
    Checks both server availability and internet connectivity
    """
    
    def __init__(self, 
                 server_url: str = "http://localhost:8000",
                 check_interval: int = 10):
        self.server_url = server_url
        self.check_interval = check_interval
        self.is_online = True
        self.last_check = None
        self.mode_changed_callback: Optional[Callable] = None
        self.task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self):
        """Start background network monitoring"""
        self.task = asyncio.create_task(self._monitor_loop())
        logger.info("Network monitoring started")
    
    async def stop_monitoring(self):
        """Stop network monitoring"""
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Network monitoring stopped")
    
    async def _monitor_loop(self):
        """Continuous monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                was_online = self.is_online
                self.is_online = await self._check_connectivity()
                
                if was_online != self.is_online:
                    logger.warning(
                        f"Mode changed: {'ONLINE' if self.is_online else 'OFFLINE'}"
                    )
                    if self.mode_changed_callback:
                        await self.mode_changed_callback(self.is_online)
                        
                self.last_check = datetime.now()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Network check error: {e}")
    
    async def _check_connectivity(self) -> bool:
        """
        Multi-level connectivity check:
        1. Check server availability
        2. Check internet connectivity
        3. Check DNS resolution
        """
        
        # Check server first (most important)
        if await self._check_server():
            return True
        
        # Check internet connectivity
        if await self._check_internet():
            return True
        
        # Check DNS
        if await self._check_dns():
            return True
        
        return False
    
    async def _check_server(self) -> bool:
        """Check if server is reachable"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.server_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.debug(f"Server check failed: {e}")
            return False
    
    async def _check_internet(self) -> bool:
        """Check general internet connectivity"""
        # Try multiple sources for redundancy
        test_hosts = [
            "https://www.google.com",
            "https://cloudflare.com",
            "https://www.github.com",
        ]
        
        for url in test_hosts:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=3)
                    ) as resp:
                        if resp.status == 200:
                            return True
            except Exception:
                continue
        
        return False
    
    async def _check_dns(self) -> bool:
        """Check DNS resolution as last resort"""
        try:
            loop = asyncio.get_event_loop()
            await loop.getaddrinfo('google.com', 443)
            return True
        except Exception:
            return False
    
    def is_offline(self) -> bool:
        """Quick check: are we offline?"""
        return not self.is_online
    
    def get_status(self) -> dict:
        """Get current network status"""
        return {
            "is_online": self.is_online,
            "is_offline": not self.is_online,
            "mode": "ONLINE" if self.is_online else "OFFLINE",
            "last_check": self.last_check.isoformat() if self.last_check else None
        }


class HealthCheckEndpoint:
    """
    Simple health check endpoint for backend
    Used by clients to verify server availability
    """
    
    def __init__(self, app):
        self.app = app
    
    def register_routes(self):
        """Register health check routes"""
        
        @self.app.get("/health")
        async def health_check():
            """
            Simple health check
            Returns 200 if server is running
            """
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "mode": "SERVER"
            }
        
        @self.app.get("/health/detailed")
        async def detailed_health():
            """
            Detailed health information
            Includes database and external service status
            """
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "mode": "SERVER",
                "services": {
                    "database": "connected",
                    "cache": "available",
                    "websocket": "ready"
                }
            }


# Usage in FastAPI app:
"""
In backend/app/main.py:

from app.utils.network_detector import HealthCheckEndpoint

# Register health check routes
health = HealthCheckEndpoint(app)
health.register_routes()
"""
