from __future__ import annotations
from collections import defaultdict, deque
from time import monotonic
from threading import Lock
from fastapi import HTTPException, Request

class SlidingWindowLimiter:
    def __init__(self):
        self.buckets: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = monotonic()
        with self.lock:
            bucket = self.buckets[key]
            while bucket and now - bucket[0] > window_seconds:
                bucket.popleft()
            if len(bucket) >= limit:
                raise HTTPException(429, "Too many requests. Please try again later.")
            bucket.append(now)

limiter = SlidingWindowLimiter()

def limit_auth(request: Request) -> None:
    limiter.check(f"auth:{request.client.host if request.client else 'unknown'}", 12, 60)

def limit_ai(request: Request) -> None:
    limiter.check(f"ai:{request.client.host if request.client else 'unknown'}", 20, 60)
