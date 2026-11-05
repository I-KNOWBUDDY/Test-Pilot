"""Test Pilot — Shared Pytest Fixtures and Session Configuration.

Configures reusable HTTP session with retry strategies, exponential backoff,
configurable base URL, explicit timeouts, and the Test Pilot APIClient.
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.api_client import APIClient

DEFAULT_BASE_URL = "https://jsonplaceholder.typicode.com"
DEFAULT_TIMEOUT_SECONDS = 10.0


@pytest.fixture(scope="session")
def base_url() -> str:
    """Retrieve the target API base URL from environment or fallback default."""
    url = os.getenv("BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
    return url


@pytest.fixture(scope="session")
def request_timeout() -> float:
    """Retrieve the per-request timeout threshold from environment."""
    timeout_raw = os.getenv("REQUEST_TIMEOUT", str(DEFAULT_TIMEOUT_SECONDS))
    try:
        return float(timeout_raw)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


@pytest.fixture(scope="session")
def retry_strategy() -> Retry:
    """Define sensible retry strategy with exponential backoff on transient network faults."""
    return Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "PUT", "DELETE", "PATCH"],
        raise_on_status=False,
    )


@pytest.fixture(scope="session")
def api_session(retry_strategy: Retry) -> Generator[requests.Session, None, None]:
    """Create a persistent requests.Session configured with connection retries and cleanup."""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "Accept": "application/json",
            "User-Agent": "Test-Pilot/0.1.0 (Automated QA Framework)",
        }
    )

    yield session

    session.close()


@pytest.fixture(scope="session")
def api_client(
    base_url: str,
    api_session: requests.Session,
    request_timeout: float,
) -> APIClient:
    """Provide an initialized Test Pilot APIClient instance for test cases."""
    return APIClient(
        base_url=base_url,
        session=api_session,
        default_timeout=request_timeout,
    )
