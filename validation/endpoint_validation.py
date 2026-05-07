from __future__ import annotations

import json
from pathlib import Path

from validation.common import (
    AI_ENDPOINTS,
    DEFAULT_ISSUE,
    REPO_ROOT,
    ValidationConfig,
    assert_auth_error_shape,
    assert_error_shape,
    assert_secure_headers,
    assert_success_shape,
    auth_headers,
    log,
    main_exit,
    request_json,
    request_with_response,
)


def validate_endpoints() -> None:
    config = ValidationConfig()
    log('endpoint_validation_start', base_url=config.base_url)

    status, body, latency, response = request_with_response('GET', '/health', config=config)
    assert_success_shape('/health', status, body)
    assert_secure_headers('/health', response)
    log('endpoint_validated', endpoint='/health', status_code=status, latency_ms=latency)

    headers = auth_headers(config)
    for endpoint in AI_ENDPOINTS:
        status, body, latency, response = request_with_response(
            'POST',
            endpoint,
            {'issue': DEFAULT_ISSUE},
            headers=headers,
            config=config,
        )
        assert_success_shape(endpoint, status, body)
        assert_secure_headers(endpoint, response)
        log('jwt_validation_passed', endpoint=endpoint, status_code=status)
        if body.get('endpoint') != endpoint:
            raise AssertionError(f'{endpoint} returned endpoint marker {body.get("endpoint")}')
        if not isinstance(body.get('response'), str) or len(body['response'].strip()) < 10:
            raise AssertionError(f'{endpoint} returned an inconsistent AI response: {body}')
        log(
            'endpoint_validated',
            endpoint=endpoint,
            status_code=status,
            latency_ms=latency,
            score=body.get('score'),
        )

        status, body, latency = request_json(
            'POST',
            endpoint,
            {'issue': ''},
            headers=headers,
            config=config,
        )
        assert_error_shape(endpoint, status, body, 400)
        log('endpoint_error_validated', endpoint=endpoint, case='empty_issue', latency_ms=latency)

    status, body, latency = request_json(
        'POST',
        '/describe',
        {'issue': DEFAULT_ISSUE},
        headers={'Content-Type': 'application/json'},
        config=config,
    )
    assert_auth_error_shape('/describe', status, body)
    log('endpoint_error_validated', endpoint='/describe', case='missing_jwt', latency_ms=latency)

    status, body, latency = request_json(
        'POST',
        '/recommend',
        {'issue': DEFAULT_ISSUE},
        headers={'Authorization': 'Bearer malformed.jwt.token', 'Content-Type': 'application/json'},
        config=config,
    )
    assert_auth_error_shape('/recommend', status, body)
    log('endpoint_error_validated', endpoint='/recommend', case='malformed_jwt', latency_ms=latency)

    fallback_cases_path = Path(REPO_ROOT / 'validation' / 'fallback_test_cases.json')
    fallback_cases = json.loads(fallback_cases_path.read_text(encoding='utf-8'))['cases']
    for case in fallback_cases:
        case_headers = {'Content-Type': 'application/json'} if case['name'] == 'missing_jwt' else headers
        status, body, latency = request_json(
            'POST',
            case['endpoint'],
            case['payload'],
            headers=case_headers,
            config=config,
        )
        if case['name'] == 'missing_jwt':
            assert_auth_error_shape(case['endpoint'], status, body)
        else:
            assert_error_shape(case['endpoint'], status, body, int(case['expected_status']))
        expected_fragment = case['expected_message_fragment'].lower()
        if expected_fragment not in str(body.get('message', '')).lower():
            raise AssertionError(f'{case["name"]} did not include expected message fragment: {body}')
        log(
            'fallback_case_validated',
            case=case['name'],
            endpoint=case['endpoint'],
            status_code=status,
            latency_ms=latency,
        )


if __name__ == '__main__':
    main_exit(validate_endpoints)
