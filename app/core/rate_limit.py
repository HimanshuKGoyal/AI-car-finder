# app/core/rate_limit.py
import time
from collections import defaultdict
from fastapi import Request, HTTPException

WINDOW = 60  # seconds
LIMIT = 120  # requests per IP per window
hits: dict[str, list[float]] = defaultdict(list)

async def rate_limit(request: Request):
    ip = request.client.host
    now = time.time()
    window_start = now - WINDOW
    bucket = hits[ip]
    # prune
    while bucket and bucket[0] < window_start:
        bucket.pop(0)
    bucket.append(now)
    if len(bucket) > LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")
