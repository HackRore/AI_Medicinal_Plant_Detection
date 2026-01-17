"""
Rate Limiting Middleware
Simple in-memory rate limiting for API endpoints
"""

import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from typing import Dict, Tuple

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit the number of requests per client IP.
    Uses in-memory storage (dict).
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Store request counts: {ip: (count, last_reset_time)}
        self.requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))
        self.limit = settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # 1 minute

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for specific paths if needed (e.g., health check)
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        client_ip = request.client.host
        current_time = time.time()
        
        count, last_reset = self.requests[client_ip]
        
        # Reset window if time expired
        if current_time - last_reset > self.window:
            count = 0
            last_reset = current_time
        
        # Increment count
        count += 1
        self.requests[client_ip] = (count, last_reset)
        
        # Check limit
        if count > self.limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
            
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.limit - count))
        response.headers["X-RateLimit-Reset"] = str(int(last_reset + self.window))
        
        return response
