from __future__ import annotations

import time
import uuid
from typing import Any

from flask import Flask, g, request

from monitoring.metrics import metrics_registry
from security.secure_logging import safe_extra


def attach_monitoring_middleware(app: Flask) -> None:
    @app.before_request
    def start_monitoring() -> None:
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        g.request_started_at = time.perf_counter()
        app.logger.info(
            'request_started',
            extra=safe_extra(
                request_id=g.request_id,
                method=request.method,
                path=request.path,
                remote_addr=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
            ),
        )

    @app.after_request
    def finish_monitoring(response: Any) -> Any:
        started_at = getattr(g, 'request_started_at', time.perf_counter())
        latency_seconds = max(0.0, time.perf_counter() - started_at)
        request_id = getattr(g, 'request_id', 'unknown')
        response.headers['X-Request-ID'] = request_id
        metrics_registry.record_request(request.method, request.path, response.status_code, latency_seconds)
        app.logger.info(
            'request_completed',
            extra=safe_extra(
                request_id=request_id,
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                latency_ms=round(latency_seconds * 1000, 2),
                content_length=response.calculate_content_length() or 0,
            ),
        )
        return response
