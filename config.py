from __future__ import annotations
import os


def _bool_env(name: str, default: str = 'false') -> bool:
    return os.getenv(name, default).lower() in ('1', 'true', 'yes')


def _int_env(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _float_env(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


class Config:
    def __init__(self) -> None:
        self.GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
        self.GROQ_API_BASE_URL: str = os.getenv('GROQ_API_BASE_URL', 'https://api.groq.com/openai/v1')
        self.GROQ_MODEL: str = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.RATE_LIMIT: str = os.getenv('RATE_LIMIT', '30 per minute')
        self.RATE_LIMIT_STORAGE_URI: str = os.getenv('RATE_LIMIT_STORAGE_URI', os.getenv('REDIS_URL', ''))
        self.REDIS_URL: str = os.getenv('REDIS_URL', '')
        self.JWT_AUTH_ENABLED: bool = os.getenv('JWT_AUTH_ENABLED', 'true').lower() in ('1', 'true', 'yes')
        self.JWT_SECRET: str = os.getenv('JWT_SECRET', '')
        self.JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
        self.JWT_AUDIENCE: str = os.getenv('JWT_AUDIENCE', '')
        self.JWT_ISSUER: str = os.getenv('JWT_ISSUER', '')
        self.ALLOWED_ORIGINS: str = os.getenv('ALLOWED_ORIGINS', 'http://localhost,http://127.0.0.1')
        self.REQUEST_TIMEOUT_SECONDS: int = _int_env('REQUEST_TIMEOUT_SECONDS', 10)
        self.AI_CACHE_ENABLED: bool = _bool_env('AI_CACHE_ENABLED', 'true')
        self.AI_CACHE_TTL_SECONDS: int = _int_env('AI_CACHE_TTL_SECONDS', 900)
        self.GROQ_MAX_RETRIES: int = _int_env('GROQ_MAX_RETRIES', 3)
        self.GROQ_BACKOFF_SECONDS: float = _float_env('GROQ_BACKOFF_SECONDS', 1.0)
        self.GROQ_TIMEOUT_SECONDS: int = _int_env('GROQ_TIMEOUT_SECONDS', 10)
        self.AI_TASK_QUEUE_ENABLED: bool = _bool_env('AI_TASK_QUEUE_ENABLED', 'true')
        self.AI_TASK_QUEUE_NAME: str = os.getenv('AI_TASK_QUEUE_NAME', 'tool125:task-queue:ai')
        self.AI_TASK_RESULT_TTL_SECONDS: int = _int_env('AI_TASK_RESULT_TTL_SECONDS', 3600)
        self.AI_TASK_MAX_ATTEMPTS: int = _int_env('AI_TASK_MAX_ATTEMPTS', 3)
        self.AI_WORKER_CONCURRENCY: int = _int_env('AI_WORKER_CONCURRENCY', 2)
        self.AI_WORKER_POLL_TIMEOUT_SECONDS: int = _int_env('AI_WORKER_POLL_TIMEOUT_SECONDS', 5)
        self.AI_WORKER_HEARTBEAT_TTL_SECONDS: int = _int_env('AI_WORKER_HEARTBEAT_TTL_SECONDS', 30)
        self.MAX_CONTENT_LENGTH: int = 16 * 1024
        self.JSONIFY_PRETTYPRINT_REGULAR = False
        self.JSON_SORT_KEYS = False

        if not self.GROQ_API_KEY:
            raise ValueError('GROQ_API_KEY must be configured in environment variables.')
        if self.JWT_AUTH_ENABLED and not self.JWT_SECRET:
            raise ValueError('JWT_SECRET must be configured in environment variables when JWT auth is enabled.')
