# Test Pilot — API Testing Framework

**Test Pilot** is an automated REST API testing and contract validation framework built with Python, pytest, requests, and jsonschema. Designed as a production-style quality assurance solution for microservices and HTTP backends, Test Pilot demonstrates robust test design, connection pooling, transient failure recovery, strict schema enforcement, and seamless continuous integration via GitHub Actions.

The framework tests against [JSONPlaceholder](https://jsonplaceholder.typicode.com) by default, while supporting dynamic redirection to internal staging or local mock environments using simple environment variables.

---

## Table of Contents

- [Purpose](#purpose)
- [Key Features](#key-features)
- [Original Improvements](#original-improvements)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Configuration](#environment-configuration)
- [Running Tests](#running-tests)
- [Test Reporting](#test-reporting)
- [Continuous Integration (CI)](#continuous-integration-ci)
- [Design Decisions & Limitations](#design-decisions--limitations)
- [Author & Portfolio Context](#author--portfolio-context)

---

## Purpose

Automated API testing is critical for validating that distributed web services deliver reliable, conformant responses across rapid release cycles. **Test Pilot** addresses key testing challenges:

1. **Contract Reliability**: Ensuring services never alter response shapes unexpectedly.
2. **Execution Stability**: Mitigating flaky tests caused by brief network hiccups using connection retries.
3. **Actionable Diagnostics**: Replacing generic assertion failures with structured error reporting that pinpoints the root cause immediately.
4. **CI/CD Readiness**: Delivering automated linting, test matrices across Python versions, and standardized JUnit XML reporting for build pipelines.

---

## Key Features

- **Reusable API Client**: Encapsulates request sessions, path normalization, explicit timeout defaults, and clean HTTP verb helpers (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
- **Resilient Connection Handling**: Employs `urllib3.util.retry.Retry` with backoff factors across HTTP status codes 429, 500, 502, 503, and 504.
- **Contract & Schema Validation**: Enforces JSON Schema (Draft-7) compliance on both individual resources and paginated collections.
- **Parameterized Test Coverage**: Tests cross-resource catalogs (`posts`, `users`, `comments`, `todos`, `albums`), relational sub-paths (e.g. `/posts/1/comments`), and query-based pagination (`_limit`).
- **Targeted Test Markers**: Organizes execution with `smoke` (rapid health checks) and `contract` (schema compliance) markers.
- **Negative & Edge Case Coverage**: Validates HTTP 404 responses for missing entities, empty responses for non-matching queries, and timeout thresholds.
- **Automated CI Workflow**: GitHub Actions workflow running tests across Python 3.9, 3.10, 3.11, 3.12, and 3.13 with Ruff code quality gates.

---

## Original Improvements

Compared to minimal boilerplate test repositories, Test Pilot introduces several practical enhancements:

1. **Diagnostic Assertion Engine (`src/validators.py`)**:
   - `validate_status_code` captures the request method, target URL, and a preview of the response body, making triage instantaneous in CI logs.
   - `validate_json_schema` isolates validation violations into a numbered summary that highlights the exact JSON path and failing value.
   - `validate_response_time` validates latency thresholds to safeguard service level agreements (SLAs).
2. **Explicit Per-Request & Default Timeouts**:
   - Eliminates the risk of hanging CI jobs by ensuring every network call enforces an explicit timeout.
3. **Structured Documentation Architecture**:
   - Dedicated [`docs/PROJECT_SUMMARY.md`](docs/PROJECT_SUMMARY.md), [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md), and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) providing comprehensive project context.
4. **Flexible Base URL Decoupling**:
   - Complete runtime portability across staging, local mock, and production endpoints via the `BASE_URL` environment variable.

---

## Technology Stack

| Component | Library / Tool | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Runtime** | Python | 3.9+ | Core programming language |
| **Test Runner** | pytest | 8.x / 9.x | Test runner, fixtures, discovery, and reporting |
| **HTTP Client** | requests | 2.31+ | Network calls, session reuse, header management |
| **Contract Validation** | jsonschema | 4.20+ | Draft-7 JSON Schema assertions |
| **Resilience** | urllib3 | 2.x | Retry adapters and connection pooling |
| **Linter / Formatter** | Ruff | 0.3+ | Fast code linting, style enforcement, and formatting |
| **CI / CD** | GitHub Actions | v4/v5 | Matrix testing across Python 3.9–3.13 |

---

## Project Structure

```text
TestPilot/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions pipeline (matrix test + lint + artifacts)
├── docs/
│   ├── ARCHITECTURE.md            # Architecture, module design, and error handling
│   ├── PROJECT_SUMMARY.md         # Executive one-page project summary
│   └── TEST_PLAN.md               # Test strategy, scope, matrix, and acceptance criteria
├── reports/
│   └── junit.xml                  # Generated JUnit XML test report
├── src/
│   ├── __init__.py                # Package exports
│   ├── api_client.py              # Reusable APIClient wrapper with explicit timeouts
│   └── validators.py              # Assertion helpers (status code, schema, latency)
├── tests/
│   ├── __init__.py                # Tests package
│   ├── conftest.py                # Shared fixtures (base_url, session, client, retries)
│   ├── schemas.py                 # JSON Schema (Draft-7) contract definitions
│   ├── test_contract.py           # Contract validation tests (@pytest.mark.contract)
│   ├── test_multi_resource_api.py # Parameterized multi-resource & relational tests
│   ├── test_negative_cases.py     # 404s, empty filters, and timeout boundary tests
│   ├── test_posts_api.py          # CRUD & filtering tests for /posts (@pytest.mark.smoke)
│   └── test_users_api.py          # User retrieval and query tests (@pytest.mark.smoke)
├── .gitignore                     # Git ignore rules for Python, virtual environments, and caches
├── pyproject.toml                 # Project metadata and Ruff linter configuration
├── pytest.ini                     # Pytest configuration, addopts, and marker registrations
├── requirements.txt               # Pinned direct dependencies
└── README.md                      # Project documentation and guide
```

---

## Installation & Setup

### Prerequisites

- Python 3.9 or higher (Python 3.12 / 3.13 recommended)
- `pip` package manager
- Internet connectivity (to access JSONPlaceholder endpoints)

### 1. Clone or Open the Repository

```bash
git clone <your-repository-url> TestPilot
cd TestPilot
```

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Environment Configuration

Test Pilot supports environment variables for dynamic runtime configuration:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `BASE_URL` | `https://jsonplaceholder.typicode.com` | Root target URL for all API calls |
| `REQUEST_TIMEOUT` | `10.0` | Default network timeout per request in seconds |

### Setting Environment Variables

**Windows (PowerShell):**
```powershell
$env:BASE_URL = "https://jsonplaceholder.typicode.com"
$env:REQUEST_TIMEOUT = "15.0"
pytest
```

**Linux / macOS (Bash):**
```bash
export BASE_URL="https://jsonplaceholder.typicode.com"
export REQUEST_TIMEOUT="15.0"
pytest
```

---

## Running Tests

### Run the Full Test Suite

Executes all 44 automated tests and outputs a test summary:
```bash
pytest
```

### Run Only Smoke Tests

Runs critical health check tests tagged with `@pytest.mark.smoke` (~1 second execution):
```bash
pytest -m smoke
```

### Run Only Contract Tests

Runs JSON Schema contract validations tagged with `@pytest.mark.contract`:
```bash
pytest -m contract
```

### Run Specific Test Files

```bash
# Run posts tests
pytest tests/test_posts_api.py

# Run users tests
pytest tests/test_users_api.py

# Run negative & boundary tests
pytest tests/test_negative_cases.py
```

### Run with Verbose Logging

```bash
pytest -v -s
```

### Run Code Quality & Linting Checks

```bash
# Check code style and rules with Ruff
ruff check .

# Check code formatting with Ruff
ruff format --check .
```

---

## Test Reporting

Test Pilot automatically outputs test execution results in standardized JUnit XML format.

- **Report Location**: `reports/junit.xml` (configured in `pytest.ini` via `--junitxml=reports/junit.xml`)
- **Compatibility**: Directly ingestible by CI servers (GitHub Actions, Jenkins, GitLab CI, Azure DevOps) to render test summary widgets and track historical pass/fail trends.

To generate a custom report path manually:
```bash
pytest --junitxml=reports/custom_report.xml
```

---

## Continuous Integration (CI)

The included GitHub Actions workflow (`.github/workflows/ci.yml`) runs automatically on all pushes and pull requests:

1. **Multi-Version Matrix**: Tests against Python `3.9`, `3.10`, `3.11`, `3.12`, and `3.13`.
2. **Automated Linting**: Executes `ruff check .` and `ruff format --check .`.
3. **Automated Testing**: Executes the entire test suite via `pytest`.
4. **Artifact Retention**: Automatically uploads the generated `reports/junit.xml` report as a build artifact retained for 14 days.

---

## Design Decisions & Limitations

1. **State Persistence in Public Mock APIs**:
   - JSONPlaceholder simulates creation (`POST`), modification (`PUT`, `PATCH`), and deletion (`DELETE`) but does not persist state mutations to a persistent database.
   - In accordance with real endpoint behavior, Test Pilot validates the immediate response code (201 Created for POST, 200 OK for PUT/PATCH/DELETE) and echoed payloads, without making flawed assumptions about subsequent lookups of newly created IDs.
2. **Network Dependency**:
   - By default, tests query live public endpoints. If running in an air-gapped or offline environment, configure `BASE_URL` to point to a local mock server (e.g. `json-server` or `Prism`).
3. **Transient Fault Handling**:
   - Connection retries are intentionally restricted to idempotent HTTP methods (`GET`, `PUT`, `DELETE`, `HEAD`, `OPTIONS`) to prevent accidental duplicate state mutations.

---

## Author & Portfolio Context

**Test Pilot** was developed as a clean, extensible demonstration of production-grade automated API testing practices. It highlights:
- Clean modular design separating client mechanics from test specifications.
- Deep schema and contract validation using modern JSON Schema standards.
- Production-readiness with automated linting, test markers, and CI matrix builds.
