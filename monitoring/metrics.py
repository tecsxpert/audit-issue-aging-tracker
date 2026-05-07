from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Iterable


def _label_value(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '')


@dataclass
class MetricsRegistry:
    started_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        with getattr(self, '_lock', threading.Lock()):
            self.request_count: dict[tuple[str, str, str], int] = {}
            self.error_count: dict[tuple[str, str, str], int] = {}
            self.request_latency_sum: dict[tuple[str, str], float] = {}
            self.request_latency_count: dict[tuple[str, str], int] = {}
            self.ai_latency_sum: dict[tuple[str, str], float] = {}
            self.ai_latency_count: dict[tuple[str, str], int] = {}
            self.ai_cache_events: dict[tuple[str, str], int] = {}

    def record_request(self, method: str, path: str, status_code: int, latency_seconds: float) -> None:
        status = str(status_code)
        route = _normalize_path(path)
        with self._lock:
            self.request_count[(method, route, status)] = self.request_count.get((method, route, status), 0) + 1
            if status_code >= 400:
                self.error_count[(method, route, status)] = self.error_count.get((method, route, status), 0) + 1
            self.request_latency_sum[(method, route)] = self.request_latency_sum.get((method, route), 0.0) + latency_seconds
            self.request_latency_count[(method, route)] = self.request_latency_count.get((method, route), 0) + 1

    def record_ai_timing(self, endpoint: str, model: str, latency_seconds: float) -> None:
        key = (_normalize_path(endpoint), model)
        with self._lock:
            self.ai_latency_sum[key] = self.ai_latency_sum.get(key, 0.0) + latency_seconds
            self.ai_latency_count[key] = self.ai_latency_count.get(key, 0) + 1

    def record_ai_cache_event(self, model: str, result: str) -> None:
        key = (model, result)
        with self._lock:
            self.ai_cache_events[key] = self.ai_cache_events.get(key, 0) + 1

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                'uptime_seconds': max(0.0, time.time() - self.started_at),
                'request_count': dict(self.request_count),
                'error_count': dict(self.error_count),
                'request_latency_sum': dict(self.request_latency_sum),
                'request_latency_count': dict(self.request_latency_count),
                'ai_latency_sum': dict(self.ai_latency_sum),
                'ai_latency_count': dict(self.ai_latency_count),
                'ai_cache_events': dict(self.ai_cache_events),
            }

    def render_prometheus(self) -> str:
        snapshot = self.snapshot()
        lines = [
            '# HELP tool125_service_uptime_seconds Service uptime in seconds.',
            '# TYPE tool125_service_uptime_seconds gauge',
            f'tool125_service_uptime_seconds {snapshot["uptime_seconds"]:.6f}',
            '# HELP tool125_http_requests_total Total HTTP requests by method, route, and status.',
            '# TYPE tool125_http_requests_total counter',
        ]
        lines.extend(_render_counter('tool125_http_requests_total', ('method', 'route', 'status'), snapshot['request_count']))
        lines.extend([
            '# HELP tool125_http_errors_total Total HTTP error responses by method, route, and status.',
            '# TYPE tool125_http_errors_total counter',
        ])
        lines.extend(_render_counter('tool125_http_errors_total', ('method', 'route', 'status'), snapshot['error_count']))
        lines.extend([
            '# HELP tool125_http_request_latency_seconds_sum Total HTTP request latency in seconds.',
            '# TYPE tool125_http_request_latency_seconds_sum counter',
        ])
        lines.extend(_render_counter('tool125_http_request_latency_seconds_sum', ('method', 'route'), snapshot['request_latency_sum']))
        lines.extend([
            '# HELP tool125_http_request_latency_seconds_count HTTP request latency sample count.',
            '# TYPE tool125_http_request_latency_seconds_count counter',
        ])
        lines.extend(_render_counter('tool125_http_request_latency_seconds_count', ('method', 'route'), snapshot['request_latency_count']))
        lines.extend([
            '# HELP tool125_ai_response_latency_seconds_sum Total Groq AI response latency in seconds.',
            '# TYPE tool125_ai_response_latency_seconds_sum counter',
        ])
        lines.extend(_render_counter('tool125_ai_response_latency_seconds_sum', ('endpoint', 'model'), snapshot['ai_latency_sum']))
        lines.extend([
            '# HELP tool125_ai_response_latency_seconds_count Groq AI response timing sample count.',
            '# TYPE tool125_ai_response_latency_seconds_count counter',
        ])
        lines.extend(_render_counter('tool125_ai_response_latency_seconds_count', ('endpoint', 'model'), snapshot['ai_latency_count']))
        lines.extend([
            '# HELP tool125_ai_cache_events_total AI cache hit and miss count.',
            '# TYPE tool125_ai_cache_events_total counter',
        ])
        lines.extend(_render_counter('tool125_ai_cache_events_total', ('model', 'result'), snapshot['ai_cache_events']))
        return '\n'.join(lines) + '\n'


def _normalize_path(path: str) -> str:
    if not path:
        return 'unknown'
    return path if path.startswith('/') else f'/{path}'


def _render_counter(name: str, labels: Iterable[str], values: object) -> list[str]:
    rendered: list[str] = []
    if not isinstance(values, dict):
        return rendered
    label_names = tuple(labels)
    for key, value in sorted(values.items(), key=lambda item: str(item[0])):
        key_values = key if isinstance(key, tuple) else (str(key),)
        label_text = ','.join(
            f'{label}="{_label_value(str(label_value))}"'
            for label, label_value in zip(label_names, key_values)
        )
        rendered.append(f'{name}{{{label_text}}} {value}')
    return rendered


metrics_registry = MetricsRegistry()
