from __future__ import annotations
import os
import pytest

os.environ.setdefault('GROQ_API_KEY', 'test-key')
os.environ.setdefault('GROQ_API_BASE_URL', 'https://api.groq.com/v1')
os.environ.setdefault('JWT_AUTH_ENABLED', 'true')
os.environ.setdefault('JWT_SECRET', 'test-secret')
os.environ.setdefault('JWT_ALGORITHM', 'HS256')
os.environ.setdefault('JWT_AUDIENCE', 'tool-125')
os.environ.setdefault('JWT_ISSUER', 'tool-125-auth')
os.environ.setdefault('ALLOWED_ORIGINS', 'http://localhost,http://127.0.0.1')

from app import create_app


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
