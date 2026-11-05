# Test Pilot — Test Plan & Strategy

## 1. Overview & Objective

The primary objective of **Test Pilot** is to ensure high test reliability, comprehensive endpoint coverage, and robust schema compliance for REST API backends. This document specifies the testing scope, test matrix, validation rules, error handling strategies, and acceptance criteria.

---

## 2. Test Scope

### 2.1 In-Scope Endpoints
- `/posts`: Full CRUD lifecycle (GET collection, GET by ID, POST create, PUT update, PATCH partial update, DELETE remove, query filtering by `userId`).
- `/users`: Account retrieval (GET collection, GET by ID, query filtering by `username` and `email`, nested address/company verification).
- `/comments`: Listing, count verification, single item retrieval, and relational child checks via `/posts/{id}/comments`.
- `/todos`: Task item schema contract verification and user association via `/users/{id}/todos`.
- `/albums`: Relational association checks via `/users/{id}/albums`.

### 2.2 Out-of-Scope / Non-Assumed Operations
Because public mock APIs like JSONPlaceholder do not persist state changes to a permanent database:
- Subsequent GET requests do not expect created IDs (e.g., ID 101) to persist permanently on the server.
- Verifications check the immediate HTTP response code (201 for POST, 200 for PUT/PATCH/DELETE) and echoed payload contents rather than database side effects.
- Direct non-existent entity lookups return 404, whereas relational filters with non-existent foreign keys legitimately return an empty array `[]` with status 200.

---

## 3. Test Classification & Markers

| Marker | Description | Typical Execution Trigger |
| :--- | :--- | :--- |
| `@pytest.mark.smoke` | High-priority health checks verifying critical path availability across core resources (`/posts`, `/users`, catalogs). | Pull requests, pre-deployment smoke checks, hourly heartbeats. |
| `@pytest.mark.contract` | Deep JSON Schema (Draft-7) assertions checking types, required keys, and entity structures. | Nightly regression runs, API version upgrades, PR approvals. |
| *(unmarked)* | Detailed functional, relational hierarchy, parameter bounds, negative cases, and timeout tests. | Comprehensive CI test matrix runs. |

---

## 4. Test Matrix

| Test Suite | File | Focus Areas | Key Assertions |
| :--- | :--- | :--- | :--- |
| **Posts API** | `tests/test_posts_api.py` | CRUD operations, query filters | Status codes (200, 201), Content-Type, payload echo, ID assignments, query filtering |
| **Users API** | `tests/test_users_api.py` | User directory, nested entities | Status code (200), address and company structures, exact username/email filters |
| **Multi-Resource** | `tests/test_multi_resource_api.py` | Cross-resource volume, relational endpoints, pagination | Parameterized counts across 5 resources, foreign key relational matching, `_limit` queries |
| **Negative Cases** | `tests/test_negative_cases.py` | 404 routes, malformed IDs, empty queries, client timeouts | 404 Not Found, empty response arrays `[]`, timeout exception propagation, assertion diagnostics |
| **Contract Checks** | `tests/test_contract.py` | JSON Schema compliance | Single & collection schemas, draft-7 validation, intentional contract violation detection |

---

## 5. Entry & Exit Criteria

### Entry Criteria
- Target base URL reachable or overridden by environment variable `BASE_URL`.
- Dependencies installed (`requests`, `pytest`, `jsonschema`, `ruff`).
- Python version 3.9 or higher.

### Exit Criteria
- 100% of automated tests pass without unhandled exceptions.
- 0 linting or formatting violations reported by Ruff.
- Valid JUnit XML report generated at `reports/junit.xml`.
- Response latency for all critical endpoints stays below SLA thresholds (< 5.0 seconds).
