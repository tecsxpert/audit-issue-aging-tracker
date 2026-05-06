from __future__ import annotations
import pytest
from test_utils import assert_success_response, assert_error_response, assert_ai_response_structure


@pytest.mark.unit
class TestGenerateReportEndpoint:
    def test_generate_report_valid_request_success(self, client, auth_headers, valid_generate_report_request, monkeypatch) -> None:
        """Test POST /generate-report with valid request returns success."""
        monkeypatch.setattr(
            'services.groq_client.GroqClient.generate',
            lambda self, prompt: 'Problem Summary.\nRoot Cause Analysis.\nRisk Level: High.\nRecommended Remediation.\nVerification Steps.',
        )
        response = client.post('/generate-report', json=valid_generate_report_request, headers=auth_headers)
        data = assert_success_response(response)
        assert_ai_response_structure(data)
        assert data['endpoint'] == '/generate-report'

    def test_generate_report_empty_issue_returns_400(self, client, auth_headers) -> None:
        """Test POST /generate-report with empty issue returns HTTP 400."""
        response = client.post('/generate-report', json={'issue': ''}, headers=auth_headers)
        assert_error_response(response, 400, 'required and must be a non-empty string')

    def test_generate_report_missing_issue_returns_400(self, client, auth_headers) -> None:
        """Test POST /generate-report with missing issue returns HTTP 400."""
        response = client.post('/generate-report', json={'severity': 'critical'}, headers=auth_headers)
        assert_error_response(response, 400, 'required and must be a non-empty string')

    def test_generate_report_invalid_json_returns_400(self, client, auth_headers) -> None:
        """Test POST /generate-report with invalid JSON returns HTTP 400."""
        response = client.post(
            '/generate-report',
            data='{"issue": missing quotes}',
            headers={**auth_headers, 'Content-Type': 'application/json'},
        )
        assert response.status_code == 400

    def test_generate_report_missing_auth_returns_401(self, client, valid_generate_report_request) -> None:
        """Test POST /generate-report without JWT returns HTTP 401."""
        response = client.post(
            '/generate-report',
            json=valid_generate_report_request,
            headers={'Content-Type': 'application/json'},
        )
        assert response.status_code == 401

    def test_generate_report_wrong_content_type_returns_400(self, client, auth_headers, valid_generate_report_request) -> None:
        """Test POST /generate-report with wrong Content-Type returns HTTP 400."""
        response = client.post(
            '/generate-report',
            json=valid_generate_report_request,
            headers={**auth_headers, 'Content-Type': 'application/xml'},
        )
        assert response.status_code == 400

    def test_generate_report_includes_risk_level_in_response(self, client, auth_headers, valid_generate_report_request, monkeypatch) -> None:
        """Test POST /generate-report response contains AI-generated content."""
        ai_response = 'Problem: Data exposure.\nRisk: Critical.\nFix: Implement encryption.'
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: ai_response)
        response = client.post('/generate-report', json=valid_generate_report_request, headers=auth_headers)
        data = assert_success_response(response)
        assert ai_response in data['response']


@pytest.mark.unit
class TestGenerateReportErrorHandling:
    def test_generate_report_groq_malformed_response(self, client, auth_headers, valid_generate_report_request, monkeypatch) -> None:
        """Test POST /generate-report handles malformed Groq response."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: None)
        response = client.post('/generate-report', json=valid_generate_report_request, headers=auth_headers)
        assert response.status_code in (200, 502)

    def test_generate_report_very_long_issue_accepted(self, client, auth_headers, monkeypatch) -> None:
        """Test POST /generate-report accepts long issue descriptions (under size limit)."""
        monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'Report output.')
        long_issue = 'A' * 10000
        response = client.post('/generate-report', json={'issue': long_issue}, headers=auth_headers)
        assert response.status_code == 200
