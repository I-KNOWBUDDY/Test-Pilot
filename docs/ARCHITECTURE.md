# Test Pilot — Architecture & Design

## 1. Architectural Philosophy

**Test Pilot** is architected to be modular, transparent, and resilient against transient network volatility while maintaining strict test determinism. Rather than relying on heavyweight BDD or complex test frameworks, Test Pilot relies on native Python idioms, standard `pytest` fixtures, and composable validation utilities.

---

## 2. Component Architecture

```
                       +-----------------------+
                       |   Pytest Test Engine   |
                       +-----------+-----------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
+------------------+                               +--------------------+
|  Shared Fixtures |                               |    Test Suites     |
| (conftest.py)    |                               | (test_*.py)        |
+--------+---------+                               +---------+----------+
         |                                                   |
         | Instantiates & Injects                            | Uses for calls & asserts
         v                                                   v
+------------------+        HTTP Requests          +--------------------+
| Test Pilot Client| ----------------------------> |  Live Target API   |
| (api_client.py)  | <---------------------------- | (JSONPlaceholder)  |
+--------+---------+        HTTP Responses         +--------------------+
         |                                                   |
         | Managed Session with Retries                      v
         | (urllib3 HTTPAdapter)                   +--------------------+
         |                                         | Assertion Engine   |
         |                                         | (validators.py)    |
         |                                         +---------+----------+
         |                                                   | Validates Against
         |                                                   v
         |                                         +--------------------+
         |                                         |    JSON Schemas    |
         |                                         | (schemas.py)       |
         +---------------------------------------> +--------------------+
```

---

## 3. Core Modules & Responsibilities

### 3.1 `src/api_client.py` — The Reusable API Client
- **URL Normalization**: Intelligently handles combinations of trailing slashes in `base_url` and leading slashes in endpoint paths to prevent broken URLs or double-slashes.
- **Explicit Timeout Enforcement**: Every network call requires a timeout. The client defaults to a configurable threshold (10.0s), preventing indefinite thread hangs during CI execution.
- **Convenience HTTP Wrappers**: Exposes clean, typed methods (`get`, `post`, `put`, `patch`, `delete`) and `get_json()`.
- **Lifecycle Management**: Implements the context manager protocol (`__enter__` and `__exit__`), automatically cleaning up underlying sockets and connection pools when owned.

### 3.2 `src/validators.py` — Diagnostic Assertion Engine
Standard assertion libraries often output generic diffs when an assertion fails. Test Pilot's custom validators provide rich context:
- **`validate_status_code`**: Outputs the HTTP method, the attempted URL, expected status code(s), actual status received, and the first 250 characters of the response body.
- **`validate_json_schema`**: Uses `jsonschema.Draft7Validator`, collects all schema violations, and formats a numbered report highlighting the exact JSON path (e.g. `user.address.geo.lat`), the failing value, and the violation reason.
- **`validate_content_type`**: Asserts correct MIME headers (e.g. `application/json`).
- **`validate_response_time`**: Asserts server response time falls within defined performance SLA boundaries.

### 3.3 `tests/conftest.py` — Fixture Orchestration
- **`base_url`**: Session-scoped fixture reading from `BASE_URL` environment variable or falling back to `https://jsonplaceholder.typicode.com`.
- **`retry_strategy`**: urllib3 `Retry` configuration with exponential backoff (`factor=0.5`), 3 maximum retries on transient errors (`429, 500, 502, 503, 504`), and safe idempotent HTTP methods.
- **`api_session`**: Creates a single reusable `requests.Session` with mounted adapters, sets default `Accept` and `User-Agent` headers, and ensures clean closure during teardown.
- **`api_client`**: Injects an initialized `APIClient` into all test functions.

### 3.4 `tests/schemas.py` — Formal Contract Definitions
Defines Draft-7 JSON Schemas representing the canonical data contracts for `/posts`, `/users`, `/comments`, and `/todos`. Includes constraints on required fields, data types, and minimum collection sizes.

---

## 4. Resilience and Error Handling

1. **Transient Fault Tolerance**: Network hiccups and intermittent 502/503/504 errors are retried automatically up to 3 times with exponential backoff before failing.
2. **Deterministic Timeouts**: Network sockets cannot block CI runners indefinitely. If an endpoint does not reply within the configured timeout, a timeout exception is raised.
3. **Graceful Contract Failure Details**: When schema violations occur, the test log provides immediate root-cause clarity rather than opaque traceback dumps.
