from __future__ import annotations

import json
import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_security_and_logging_middleware(app: FastAPI, logger: logging.Logger) -> None:
    request_counters: dict[str, dict[str, int]] = defaultdict(dict)

    @app.middleware("http")
    async def security_and_logging(request: Request, call_next):
        start = time.perf_counter()
        request_id = str(uuid.uuid4())
        now_bucket = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M")
        client_ip = request.client.host if request.client else "unknown"
        counter_key = f"{client_ip}:{now_bucket}"
        _prune_rate_limit_buckets(request_counters, keep_last=3)

        api_key = os.getenv("BASIC_AUTH_API_KEY", "")
        if api_key:
            provided = request.headers.get("x-api-key", "")
            if provided != api_key:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        current = request_counters[now_bucket].get(counter_key, 0)
        if current >= limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        request_counters[now_bucket][counter_key] = current + 1

        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "client_ip": client_ip,
                    "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            )
        )
        return response


def _prune_rate_limit_buckets(counters: dict[str, dict[str, int]], keep_last: int = 3) -> None:
    if len(counters) <= keep_last:
        return
    for bucket in sorted(counters.keys())[:-keep_last]:
        counters.pop(bucket, None)
