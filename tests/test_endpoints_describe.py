from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest
from test_utils import assert_success_response, assert_error_response, assert_ai_response_structure


@pytest.mark.unit
class TestDescribeEndpoint:
    def test_describe_valid_request_success(self, client, auth_headers, valid_describe_request, monkeypatch) -> None:
        """Test POST /describe with valid request returns success."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Audit analysis response.')
        response = client.post('/describe', json=valid_describe_request, headers=auth_headers)
        data = assert_success_response(response)
        assert_ai_response_structure(data)
        assert data['endpoint'] == '/describe'

    def test_describe_empty_issue_returns_400(self, client, auth_headers) -> None:
        """Test POST /describe with empty issue returns HTTP 400."""
        response = client.post('/describe', json={'issue': ''}, headers=auth_headers)
        assert_error_response(response, 400, 'required and must be a non-empty string')

    def test_describe_missing_issue_field_returns_400(self, client, auth_headers) -> None:
        """Test POST /describe with missing issue field returns HTTP 400."""
        response = client.post('/describe', json={}, headers=auth_headers)
        assert_error_response(response, 400, 'required and must be a non-empty string')

    def test_describe_invalid_json_returns_400(self, client, auth_headers) -> None:
        """Test POST /describe with malformed JSON returns HTTP 400."""
        response = client.post(
            '/describe',
            data='{invalid json}',
            headers={**auth_headers, 'Content-Type': 'application/json'},
        )
        assert response.status_code == 400

    def test_describe_wrong_content_type_returns_400(self, client, auth_headers, valid_describe_request) -> None:
        """Test POST /describe with wrong Content-Type returns HTTP 400."""
        response = client.post(
            '/describe',
            json=valid_describe_request,
            headers={**auth_headers, 'Content-Type': 'text/plain'},
        )
        assert response.status_code == 400

    def test_describe_missing_auth_returns_401(self, client, valid_describe_request) -> None:
        """Test POST /describe without JWT returns HTTP 401."""
        response = client.post(
            '/describe',
            json=valid_describe_request,
            headers={'Content-Type': 'application/json'},
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['status'] == 'error'

    def test_describe_invalid_jwt_returns_401(self, client, invalid_jwt_token, valid_describe_request) -> None:
        """Test POST /describe with invalid JWT returns HTTP 401."""
        response = client.post(
            '/describe',
            json=valid_describe_request,
            headers={'Authorization': f'Bearer {invalid_jwt_token}', 'Content-Type': 'application/json'},
        )
        assert response.status_code == 401

    def test_describe_response_includes_score(self, client, auth_headers, valid_describe_request, monkeypatch) -> None:
        """Test POST /describe response includes quality score."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Comprehensive audit analysis with multiple sentences. Risk assessment included.')
        response = client.post('/describe', json=valid_describe_request, headers=auth_headers)
        data = assert_success_response(response)
        assert 'score' in data
        assert isinstance(data['score'], int)
        assert 1 <= data['score'] <= 10


@pytest.mark.unit
class TestDescribeErrorHandling:
    def test_describe_groq_api_failure_returns_502(self, client, auth_headers, valid_describe_request, monkeypatch) -> None:
        """Test POST /describe when Groq API fails returns HTTP 502."""
        from services.groq_client import GroqClientError
        monkeypatch.setattr(
            'services.groq_client.GroqClient.generate',
            lambda self, prompt: (_ for _ in ()).throw(GroqClientError('API unavailable')),
        )
        response = client.post('/describe', json=valid_describe_request, headers=auth_headers)
        assert_error_response(response, 502, 'Groq API failed')

    def test_describe_with_whitespace_only_issue_returns_400(self, client, auth_headers) -> None:
        """Test POST /describe with whitespace-only issue returns HTTP 400."""
        response = client.post('/describe', json={'issue': '   \t\n  '}, headers=auth_headers)
        assert response.status_code == 400
