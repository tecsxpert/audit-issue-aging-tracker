from __future__ import annotations
import pytest
from test_utils import assert_success_response, assert_json_response, assert_ai_response_structure


@pytest.mark.unit
class TestResponseFormatValidation:
    def test_describe_response_includes_all_fields(self, client, auth_headers, valid_describe_request, monkeypatch) -> None:
        """Test /describe response includes all required fields."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Analysis result.')
        response = client.post('/describe', json=valid_describe_request, headers=auth_headers)
        data = assert_success_response(response)
        assert 'status' in data
        assert 'endpoint' in data
        assert 'issue' in data
        assert 'response' in data
        assert 'score' in data

    def test_recommend_response_includes_all_fields(self, client, auth_headers, valid_recommend_request, monkeypatch) -> None:
        """Test /recommend response includes all required fields."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Recommendations here.')
        response = client.post('/recommend', json=valid_recommend_request, headers=auth_headers)
        data = assert_success_response(response)
        assert_ai_response_structure(data)
        assert data['endpoint'] == '/recommend'

    def test_generate_report_response_includes_all_fields(self, client, auth_headers, valid_generate_report_request, monkeypatch) -> None:
        """Test /generate-report response includes all required fields."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Full report here.')
        response = client.post('/generate-report', json=valid_generate_report_request, headers=auth_headers)
        data = assert_success_response(response)
        assert_ai_response_structure(data)
        assert data['endpoint'] == '/generate-report'

    def test_health_response_format(self, client) -> None:
        """Test /health response has correct format."""
        response = client.get('/health')
        data = assert_json_response(response)
        assert data['status'] == 'ok'
        assert 'services' in data
        assert isinstance(data['services'], list)


@pytest.mark.unit
class TestResponseDataTypes:
    def test_ai_response_fields_are_correct_types(self, client, auth_headers, valid_describe_request, monkeypatch) -> None:
        """Test AI response fields are correct data types."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Response text.')
        response = client.post('/describe', json=valid_describe_request, headers=auth_headers)
        data = assert_success_response(response)
        assert isinstance(data['status'], str)
        assert isinstance(data['endpoint'], str)
        assert isinstance(data['issue'], str)
        assert isinstance(data['response'], str)
        assert isinstance(data['score'], int)

    def test_score_is_in_valid_range(self, client, auth_headers, valid_describe_request, monkeypatch) -> None:
        """Test score field is between 1 and 10."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Analysis with multiple sentences and keywords like risk and recommend.')
        response = client.post('/describe', json=valid_describe_request, headers=auth_headers)
        data = assert_success_response(response)
        assert 1 <= data['score'] <= 10

    def test_endpoint_field_matches_requested_endpoint(self, client, auth_headers, valid_describe_request, monkeypatch) -> None:
        """Test endpoint field matches the actual endpoint called."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Response.')
        
        response1 = client.post('/describe', json=valid_describe_request, headers=auth_headers)
        assert response1.get_json()['endpoint'] == '/describe'
        
        response2 = client.post('/recommend', json=valid_describe_request, headers=auth_headers)
        assert response2.get_json()['endpoint'] == '/recommend'
        
        response3 = client.post('/generate-report', json=valid_describe_request, headers=auth_headers)
        assert response3.get_json()['endpoint'] == '/generate-report'


@pytest.mark.unit
class TestErrorResponseFormat:
    def test_error_response_has_status_field(self, client, auth_headers) -> None:
        """Test error response always includes status field."""
        response = client.post('/describe', json={'issue': ''}, headers=auth_headers)
        data = assert_json_response(response)
        assert data['status'] == 'error'

    def test_error_response_has_message_field(self, client, auth_headers) -> None:
        """Test error response always includes message field."""
        response = client.post('/describe', json={}, headers=auth_headers)
        data = assert_json_response(response)
        assert 'message' in data
        assert isinstance(data['message'], str)
        assert len(data['message']) > 0

    def test_http_401_error_format(self, client, valid_describe_request) -> None:
        """Test HTTP 401 error response format."""
        response = client.post('/describe', json=valid_describe_request, headers={'Content-Type': 'application/json'})
        assert response.status_code == 401
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'message' in data

    def test_http_400_error_format(self, client, auth_headers) -> None:
        """Test HTTP 400 error response format."""
        response = client.post('/describe', json={'issue': ''}, headers=auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'message' in data

    def test_http_502_error_format(self, client, auth_headers, valid_describe_request, monkeypatch) -> None:
        """Test HTTP 502 error response format."""
        from services.groq_client import GroqClientError
        monkeypatch.setattr(
            'services.groq_client.GroqClient.generate',
            lambda self, prompt: (_ for _ in ()).throw(GroqClientError('API failed')),
        )
        response = client.post('/describe', json=valid_describe_request, headers=auth_headers)
        assert response.status_code == 502
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'message' in data
