# Test Pilot — Project Summary

## Executive Summary

**Test Pilot** is an automated REST API testing and contract validation framework developed with Python, pytest, requests, and jsonschema. Designed with production-grade QA standards in mind, Test Pilot provides structured, deterministic testing for distributed HTTP services with robust connection pooling, automatic transient fault recovery, schema integrity enforcement, and continuous integration pipeline automation.

The default test target is [JSONPlaceholder](https://jsonplaceholder.typicode.com), a widely adopted mock REST service, but Test Pilot is fully decoupled from any specific host through environment-driven base URL configuration.

---

## Key Highlights & Capabilities

- **Reusable API Client Layer (`APIClient`)**: Encapsulates session lifecycles, URL normalization, HTTP verb wrappers (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), and mandatory per-request timeout defaults.
- **Resilient Connection Handling**: Mounts `urllib3.util.retry.Retry` with exponential backoff (`status_forcelist=[429, 500, 502, 503, 504]`) to absorb temporary network jitter without masking genuine failures.
- **Contract & Schema Validation**: Enforces JSON Schema (Draft-7) standards across single resources and collection responses (`posts`, `users`, `comments`, `todos`), validating data structure, required fields, and nested entity integrity.
- **Rich Failure Diagnostics**: Custom validator helpers (`src/validators.py`) capture and report exact JSON paths, expected vs. actual status codes, request URLs, and response body snippets when assertions fail.
- **Granular Test Categorization**: Tagged with pytest markers (`smoke` for critical path health checks, `contract` for schema adherence) allowing targeted sub-second test execution.
- **Enterprise-Ready CI Integration**: GitHub Actions workflow verifies linting and formatting via Ruff across Python 3.9 through 3.13, runs the full test matrix, and produces downloadable JUnit XML test reports.

---

## Technical Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ (Tested through 3.13) | Core programming language |
| **Test Runner** | pytest 8.x / 9.x | Test orchestration, discovery, and execution |
| **HTTP Client** | requests 2.31+ | Network calls, session reuse, header management |
| **Contract Engine** | jsonschema 4.20+ | Draft-7 JSON schema specification and validation |
| **Resilience** | urllib3 | Retry adapters, backoff calculation, pool management |
| **Code Quality** | Ruff | Ultra-fast linting, import sorting, and code formatting |
| **CI / Automation** | GitHub Actions | Automated build, matrix testing, and JUnit artifact generation |

---

## Test Suite Metrics

- **Total Test Cases**: 44 automated tests
- **Smoke Tests**: 10 tests (~1.0s runtime)
- **Contract Tests**: 7 tests (~0.8s runtime)
- **Parameterized Resource Tests**: 16 tests covering 5 distinct REST resources
- **Negative & Boundary Tests**: 11 tests verifying 404s, empty filters, and timeouts
- **Average Suite Execution Time**: ~3.4 seconds across live public endpoints
