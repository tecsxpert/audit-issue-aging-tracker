# PII Masking Guide

## Purpose
This guide explains how Tool-125 prevents sensitive data from reaching prompts, logs, or API responses.

## Detection API
Use `services.pii_detector` for simple string checks:

```python
from services.pii_detector import contains_pii, mask_pii

contains_pii("admin@example.com")
mask_pii("admin@example.com")
```

Use `services.sensitive_scanner` for recursive payload scanning:

```python
from services.sensitive_scanner import scan_payload, mask_sensitive_payload

findings = scan_payload({"token": "abc", "issue": "admin@example.com"})
masked = mask_sensitive_payload({"token": "abc", "issue": "admin@example.com"})
```

## Logging
Application logging attaches `SensitiveDataFilter`, which masks:

- PII in log messages
- PII in tuple/dict log args
- PII in structured extras such as `payload_snippet`
- secret-like keys such as `token`, `password`, `api_key`, and `jwt_secret`

## Operational Rule
Do not log full request bodies. If a payload sample is needed for attack analysis, log only a short masked snippet.
