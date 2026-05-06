from __future__ import annotations
import pytest
from test_utils import assert_json_response


@pytest.mark.unit
class TestHealthEndpoint:
    def test_health_endpoint_returns_200(self, client) -> None:
        """Test GET /health returns HTTP 200."""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client) -> None:
        """Test GET /health returns valid JSON."""
        response = client.get('/health')
        data = assert_json_response(response)
        assert isinstance(data, dict)

    def test_health_endpoint_has_status_ok(self, client) -> None:
        """Test GET /health returns status: ok."""
        response = client.get('/health')
        data = response.get_json()
        assert data.get('status') == 'ok'

    def test_health_endpoint_has_services_list(self, client) -> None:
        """Test GET /health returns services list."""
        response = client.get('/health')
        data = response.get_json()
        assert 'services' in data
        assert isinstance(data['services'], list)
        assert len(data['services']) > 0

    def test_health_no_auth_required(self, client) -> None:
        """Test GET /health does not require JWT authentication."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.get_json()['status'] == 'ok'

    def test_health_endpoint_accessible_without_auth_headers(self, client) -> None:
        """Test GET /health accessible without any authentication headers."""
        response = client.get('/health', headers={})
        assert response.status_code == 200

    def test_health_endpoint_is_idempotent(self, client) -> None:
        """Test GET /health can be called multiple times with same result."""
        response1 = client.get('/health')
        response2 = client.get('/health')
        body1 = response1.get_json()
        body2 = response2.get_json()
        body1.pop('generated_at', None)
        body2.pop('generated_at', None)
        assert body1 == body2

    def test_health_endpoint_methods(self, client) -> None:
        """Test GET /health only accepts GET method."""
        post_response = client.post('/health')
        assert post_response.status_code == 405
