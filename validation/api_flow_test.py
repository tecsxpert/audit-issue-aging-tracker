from __future__ import annotations

from validation.common import (
    DEFAULT_ISSUE,
    ValidationConfig,
    assert_success_shape,
    auth_headers,
    log,
    main_exit,
    request_json,
)


def run_api_flow() -> None:
    config = ValidationConfig()
    headers = auth_headers(config)
    flow_issue = DEFAULT_ISSUE
    outputs: dict[str, str] = {}

    for endpoint in ('/describe', '/recommend', '/generate-report'):
        status, body, latency = request_json(
            'POST',
            endpoint,
            {'issue': flow_issue},
            headers=headers,
            config=config,
        )
        assert_success_shape(endpoint, status, body)
        log('jwt_validation_passed', endpoint=endpoint, status_code=status)
        outputs[endpoint] = body['response']
        log('api_flow_step_passed', endpoint=endpoint, latency_ms=latency, score=body.get('score'))

    if len(set(value.strip() for value in outputs.values())) < 2:
        raise AssertionError('AI flow responses are unexpectedly identical across all endpoints.')

    report_response = outputs['/generate-report'].lower()
    expected_terms = ('audit', 'risk', 'issue')
    if not any(term in report_response for term in expected_terms):
        raise AssertionError('Generated report response does not appear audit-focused.')

    log('api_flow_passed', endpoints=list(outputs))


if __name__ == '__main__':
    main_exit(run_api_flow)
