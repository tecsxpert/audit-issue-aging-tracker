from __future__ import annotations
import os


class Config:
    def __init__(self) -> None:
        self.GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
        self.GROQ_API_BASE_URL: str = os.getenv('GROQ_API_BASE_URL', 'https://api.groq.com/v1')
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
        self.REQUEST_TIMEOUT_SECONDS: int = int(os.getenv('REQUEST_TIMEOUT_SECONDS', '10'))
        self.MAX_CONTENT_LENGTH: int = 16 * 1024
        self.JSONIFY_PRETTYPRINT_REGULAR = False
        self.JSON_SORT_KEYS = False

        if not self.GROQ_API_KEY:
            raise ValueError('GROQ_API_KEY must be configured in environment variables.')
        if self.JWT_AUTH_ENABLED and not self.JWT_SECRET:
            raise ValueError('JWT_SECRET must be configured in environment variables when JWT auth is enabled.')
