from __future__ import annotations
from unittest.mock import patch
import pytest
from test_utils import assert_success_response, assert_error_response, assert_ai_response_structure


@pytest.mark.unit
class TestRecommendEndpoint:
    def test_recommend_valid_request_success(self, client, auth_headers, valid_recommend_request, monkeypatch) -> None:
        """Test POST /recommend with valid request returns success."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Recommendation 1. Recommendation 2. Recommendation 3.')
        response = client.post('/recommend', json=valid_recommend_request, headers=auth_headers)
        data = assert_success_response(response)
        assert_ai_response_structure(data)
        assert data['endpoint'] == '/recommend'

    def test_recommend_empty_issue_returns_400(self, client, auth_headers) -> None:
        """Test POST /recommend with empty issue returns HTTP 400."""
        response = client.post('/recommend', json={'issue': ''}, headers=auth_headers)
        assert_error_response(response, 400, 'required and must be a non-empty string')

    def test_recommend_missing_issue_field_returns_400(self, client, auth_headers) -> None:
        """Test POST /recommend with missing issue field returns HTTP 400."""
        response = client.post('/recommend', json={}, headers=auth_headers)
        assert_error_response(response, 400, 'required and must be a non-empty string')

    def test_recommend_invalid_json_returns_400(self, client, auth_headers) -> None:
        """Test POST /recommend with malformed JSON returns HTTP 400."""
        response = client.post(
            '/recommend',
            data='{unclosed": "json",}',
            headers={**auth_headers, 'Content-Type': 'application/json'},
        )
        assert response.status_code == 400

    def test_recommend_missing_auth_returns_401(self, client, valid_recommend_request) -> None:
        """Test POST /recommend without JWT returns HTTP 401."""
        response = client.post(
            '/recommend',
            json=valid_recommend_request,
            headers={'Content-Type': 'application/json'},
        )
        assert response.status_code == 401

    def test_recommend_expired_jwt_returns_401(self, client, expired_jwt_token, valid_recommend_request) -> None:
        """Test POST /recommend with expired JWT returns HTTP 401."""
        response = client.post(
            '/recommend',
            json=valid_recommend_request,
            headers={'Authorization': f'Bearer {expired_jwt_token}', 'Content-Type': 'application/json'},
        )
        assert response.status_code == 401

    def test_recommend_response_has_correct_endpoint_field(self, client, auth_headers, valid_recommend_request, monkeypatch) -> None:
        """Test POST /recommend response has correct endpoint field."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Fixed recommendations here.')
        response = client.post('/recommend', json=valid_recommend_request, headers=auth_headers)
        data = assert_success_response(response)
        assert data['endpoint'] == '/recommend'


@pytest.mark.unit
class TestRecommendErrorHandling:
    def test_recommend_groq_timeout(self, client, auth_headers, valid_recommend_request, monkeypatch) -> None:
        """Test POST /recommend handles Groq timeout gracefully."""
        from services.groq_client import GroqClientError
        monkeypatch.setattr(
            'services.groq_client.GroqClient.generate',
            lambda self, prompt: (_ for _ in ()).throw(GroqClientError('Request timed out after 3 retries.')),
        )
        response = client.post('/recommend', json=valid_recommend_request, headers=auth_headers)
        assert response.status_code == 502
        data = response.get_json()
        assert data['status'] == 'error'

    def test_recommend_with_extra_fields_ignores_them(self, client, auth_headers, valid_recommend_request, monkeypatch) -> None:
        """Test POST /recommend with extra fields is accepted."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Response.')
        payload = {**valid_recommend_request, 'extra_field': 'should be ignored', 'another': 123}
        response = client.post('/recommend', json=payload, headers=auth_headers)
        assert response.status_code == 200
