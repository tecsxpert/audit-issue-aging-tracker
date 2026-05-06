from __future__ import annotations
from unittest.mock import patch
import pytest
from test_utils import assert_error_response, assert_json_response


@pytest.mark.unit
class TestGroqClientErrorHandling:
    def test_groq_unavailable_returns_502(self, client, auth_headers, monkeypatch) -> None:
        """Test Groq API unavailable returns HTTP 502."""
        from services.groq_client import GroqClientError
        monkeypatch.setattr(
            'services.groq_client.GroqClient.generate',
            lambda self, prompt: (_ for _ in ()).throw(GroqClientError('Connection refused')),
        )
        response = client.post('/describe', json={'issue': 'Valid issue.'}, headers=auth_headers)
        assert response.status_code == 502

    def test_groq_timeout_returns_502(self, client, auth_headers, monkeypatch) -> None:
        """Test Groq timeout is retried and returns 502 after max attempts."""
        from services.groq_client import GroqClientError
        monkeypatch.setattr(
            'services.groq_client.GroqClient.generate',
            lambda self, prompt: (_ for _ in ()).throw(GroqClientError('Request timed out after 3 retries.')),
        )
        response = client.post('/recommend', json={'issue': 'Valid issue.'}, headers=auth_headers)
        assert response.status_code == 502
        data = response.get_json()
        assert 'timeout' in data['message'].lower() or 'failed' in data['message'].lower()

    def test_groq_rate_limit_returns_502(self, client, auth_headers, monkeypatch) -> None:
        """Test Groq rate limit error returns HTTP 502."""
        from services.groq_client import GroqClientError
        monkeypatch.setattr(
            'services.groq_client.GroqClient.generate',
            lambda self, prompt: (_ for _ in ()).throw(GroqClientError('Rate limit exceeded')),
        )
        response = client.post('/generate-report', json={'issue': 'Valid issue.'}, headers=auth_headers)
        assert response.status_code == 502


@pytest.mark.unit
class TestMalformedResponseHandling:
    def test_groq_returns_none_handled(self, client, auth_headers, monkeypatch) -> None:
        """Test when Groq returns None response is handled."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: None)
        response = client.post('/describe', json={'issue': 'Valid issue.'}, headers=auth_headers)
        assert response.status_code in (200, 502)

    def test_groq_returns_empty_string(self, client, auth_headers, monkeypatch) -> None:
        """Test when Groq returns empty string."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: '')
        response = client.post('/recommend', json={'issue': 'Valid issue.'}, headers=auth_headers)
        data = assert_json_response(response)
        assert response.status_code == 502
        assert data['success'] is False


@pytest.mark.unit
class TestJWTValidationErrors:
    def test_malformed_bearer_token_returns_401(self, client, valid_describe_request) -> None:
        """Test malformed Bearer token returns HTTP 401."""
        response = client.post(
            '/describe',
            json=valid_describe_request,
            headers={'Authorization': 'Bearer', 'Content-Type': 'application/json'},
        )
        assert response.status_code == 401

    def test_bearer_token_without_space_returns_401(self, client, valid_describe_request, invalid_jwt_token) -> None:
        """Test Bearer token without proper format returns HTTP 401."""
        response = client.post(
            '/describe',
            json=valid_describe_request,
            headers={'Authorization': f'Bearer{invalid_jwt_token}', 'Content-Type': 'application/json'},
        )
        assert response.status_code == 401

    def test_different_auth_scheme_returns_401(self, client, valid_describe_request) -> None:
        """Test non-Bearer auth scheme returns HTTP 401."""
        response = client.post(
            '/describe',
            json=valid_describe_request,
            headers={'Authorization': 'Basic dXNlcjpwYXNz', 'Content-Type': 'application/json'},
        )
        assert response.status_code == 401


@pytest.mark.unit
class TestRequestValidationErrors:
    def test_non_json_content_type_returns_400(self, client, auth_headers, valid_describe_request) -> None:
        """Test non-JSON content type returns HTTP 400."""
        response = client.post(
            '/describe',
            json=valid_describe_request,
            headers={**auth_headers, 'Content-Type': 'application/x-www-form-urlencoded'},
        )
        assert response.status_code == 400

    def test_missing_content_type_returns_400(self, client, auth_headers, valid_describe_request) -> None:
        """Test missing content type header returns HTTP 400."""
        response = client.post(
            '/describe',
            data='{"issue": "test"}',
            headers={'Authorization': auth_headers['Authorization']},
        )
        assert response.status_code == 400

    def test_extra_fields_in_payload_accepted(self, client, auth_headers, monkeypatch) -> None:
        """Test extra fields in payload are ignored."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Response.')
        response = client.post(
            '/describe',
            json={'issue': 'Valid issue.', 'extra': 'field', 'another': 123},
            headers=auth_headers,
        )
        assert response.status_code == 200
