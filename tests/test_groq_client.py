from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest
from services.groq_client import GroqClient, GroqClientError


@pytest.mark.unit
class TestGroqClientInitialization:
    def test_groq_client_requires_api_key(self) -> None:
        """Test GroqClient raises ValueError without API key."""
        with pytest.raises(ValueError, match='GROQ_API_KEY must be configured'):
            GroqClient(api_key='', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')

    def test_groq_client_initializes_with_valid_key(self) -> None:
        """Test GroqClient initializes successfully with API key."""
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        assert client.api_key == 'test-key'
        assert client.model == 'llama-3.3-70b-versatile'

    def test_groq_client_uses_provided_base_url(self) -> None:
        """Test GroqClient uses provided base URL."""
        client = GroqClient(
            api_key='test-key',
            base_url='https://custom.api.groq.com/v2',
            model='llama-3.3-70b-versatile',
        )
        assert client.base_url == 'https://custom.api.groq.com/v2'


@pytest.mark.unit
class TestGroqClientGeneration:
    def test_groq_client_generate_returns_string(self, monkeypatch) -> None:
        """Test GroqClient.generate returns string response."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'output': 'Generated text response.'}
        mock_session.post.return_value = mock_response
        
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        client.session = mock_session
        
        result = client.generate('Test prompt')
        assert isinstance(result, str)
        assert result == 'Generated text response.'

    def test_groq_client_generate_empty_prompt_raises_error(self) -> None:
        """Test GroqClient.generate raises error for empty prompt."""
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        with pytest.raises(ValueError, match='Prompt cannot be empty'):
            client.generate('')

    def test_groq_client_handles_json_response(self, monkeypatch) -> None:
        """Test GroqClient handles JSON-formatted responses."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'output': '{"analysis": "structured result"}'}
        mock_session.post.return_value = mock_response
        
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        client.session = mock_session
        
        result = client.generate('Test')
        assert isinstance(result, str)


@pytest.mark.unit
class TestGroqClientRetryLogic:
    def test_groq_client_retries_on_failure(self, monkeypatch) -> None:
        """Test GroqClient retries on transient failures."""
        import time
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'output': 'Success after retry.'}
        mock_session.post.side_effect = [
            ConnectionError('Connection failed'),
            ConnectionError('Connection failed'),
            mock_response,
        ]
        
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        client.session = mock_session
        
        result = client.generate('Test prompt')
        assert result == 'Success after retry.'
        assert mock_session.post.call_count == 3

    def test_groq_client_raises_after_max_retries(self, monkeypatch) -> None:
        """Test GroqClient raises error after max retries exceeded."""
        mock_session = MagicMock()
        mock_session.post.side_effect = ConnectionError('Always fails')
        
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        client.session = mock_session
        
        with pytest.raises(GroqClientError, match='Groq API failed after 3 attempts'):
            client.generate('Test prompt')


@pytest.mark.unit
class TestGroqClientErrorHandling:
    def test_groq_client_handles_http_errors(self, monkeypatch) -> None:
        """Test GroqClient handles HTTP error responses."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_session.post.return_value = mock_response
        
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        client.session = mock_session
        
        with pytest.raises(GroqClientError):
            client.generate('Test')

    def test_groq_client_handles_malformed_json(self, monkeypatch) -> None:
        """Test GroqClient handles malformed JSON responses."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_session.post.return_value = mock_response
        
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        client.session = mock_session
        
        with pytest.raises(GroqClientError):
            client.generate('Test')

    def test_groq_client_handles_missing_output_field(self, monkeypatch) -> None:
        """Test GroqClient handles response without output field."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'no output field'}
        mock_session.post.return_value = mock_response
        
        client = GroqClient(api_key='test-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
        client.session = mock_session
        
        with pytest.raises(GroqClientError):
            client.generate('Test')
