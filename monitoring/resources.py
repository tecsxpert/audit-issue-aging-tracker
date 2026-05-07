from __future__ import annotations

import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Any


def get_resource_snapshot() -> dict[str, Any]:
    memory = _memory_snapshot()
    cpu = _cpu_snapshot()
    container = _container_snapshot()
    status = 'ok' if memory['available'] or cpu['available'] or container['available'] else 'limited'
    return {
        'status': status,
        'process': {
            'pid': os.getpid(),
            'memory_rss_bytes': memory['rss_bytes'],
            'cpu_percent': cpu['cpu_percent'],
        },
        'container': container,
        'generated_at_epoch': time.time(),
    }


def _memory_snapshot() -> dict[str, Any]:
    psutil = _optional_psutil()
    if psutil is not None:
        process = psutil.Process(os.getpid())
        return {'available': True, 'rss_bytes': int(process.memory_info().rss)}
    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF)
        multiplier = 1024 if os.name != 'darwin' else 1
        return {'available': True, 'rss_bytes': int(usage.ru_maxrss * multiplier)}
    except Exception:
        return {'available': False, 'rss_bytes': None}


def _cpu_snapshot() -> dict[str, Any]:
    psutil = _optional_psutil()
    if psutil is not None:
        try:
            return {'available': True, 'cpu_percent': float(psutil.Process(os.getpid()).cpu_percent(interval=0.0))}
        except Exception:
            return {'available': False, 'cpu_percent': None}
    load_avg = getattr(os, 'getloadavg', None)
    if callable(load_avg):
        try:
            one_minute, _, _ = load_avg()
            cpu_count = os.cpu_count() or 1
            return {'available': True, 'cpu_percent': round((one_minute / cpu_count) * 100, 2)}
        except Exception:
            pass
    return {'available': False, 'cpu_percent': None}


def _container_snapshot() -> dict[str, Any]:
    memory_current = _read_int('/sys/fs/cgroup/memory.current')
    memory_max = _read_int('/sys/fs/cgroup/memory.max')
    cpu_stat = _read_text('/sys/fs/cgroup/cpu.stat')
    return {
        'available': memory_current is not None or cpu_stat is not None,
        'memory_current_bytes': memory_current,
        'memory_limit_bytes': memory_max,
        'cpu_stat_available': cpu_stat is not None,
    }


def _read_int(path: str) -> int | None:
    text = _read_text(path)
    if text is None or text == 'max':
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _read_text(path: str) -> str | None:
    try:
        return Path(path).read_text(encoding='utf-8').strip()
    except OSError:
        return None


@lru_cache(maxsize=1)
def _optional_psutil() -> Any | None:
    try:
        import psutil

        return psutil
    except Exception:
        return None
