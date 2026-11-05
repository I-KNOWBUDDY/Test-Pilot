"""Test Pilot — Reusable REST API Client.

Provides an intuitive, robust client wrapper around requests.Session with
explicit timeouts, path formatting, error handling, and session lifecycle management.
"""

from __future__ import annotations

from typing import Any

import requests


class APIClient:
    """Reusable HTTP client wrapper for automated API testing in Test Pilot.

    Encapsulates base URL handling, session state, explicit request timeouts,
    and HTTP verbs for clear, concise test specifications.
    """

    def __init__(
        self,
        base_url: str,
        session: requests.Session | None = None,
        default_timeout: float = 10.0,
    ) -> None:
        """Initialize the API client.

        Args:
            base_url: Root URL for target endpoints (e.g. https://jsonplaceholder.typicode.com).
            session: Optional pre-configured requests.Session (e.g. with retries).
            default_timeout: Default timeout in seconds applied to all network calls.
        """
        self.base_url = base_url.rstrip("/")
        self._owned_session = session is None
        self.session = session if session is not None else requests.Session()
        self.default_timeout = default_timeout

    def build_url(self, endpoint: str) -> str:
        """Construct full URL from endpoint, correctly preserving slashes.

        Args:
            endpoint: Relative or absolute path (e.g. '/posts' or 'users/1').

        Returns:
            Fully-qualified target URL string.
        """
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        clean_endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{clean_endpoint}"

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send an HTTP request with explicit timeout enforcement.

        Args:
            method: HTTP method (e.g. 'GET', 'POST', 'PUT', 'DELETE').
            endpoint: Resource path or full URL.
            timeout: Optional per-request timeout in seconds (falls back to default_timeout).
            **kwargs: Additional parameters forwarded to requests.Session.request.

        Returns:
            requests.Response object returned by the server.
        """
        url = self.build_url(endpoint)
        effective_timeout = self.default_timeout if timeout is None else timeout
        return self.session.request(
            method=method.upper(),
            url=url,
            timeout=effective_timeout,
            **kwargs,
        )

    def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Execute a GET request."""
        return self.request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Execute a POST request."""
        return self.request(
            "POST",
            endpoint,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def put(
        self,
        endpoint: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Execute a PUT request."""
        return self.request(
            "PUT",
            endpoint,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def patch(
        self,
        endpoint: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Execute a PATCH request."""
        return self.request(
            "PATCH",
            endpoint,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def delete(
        self,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Execute a DELETE request."""
        return self.request(
            "DELETE",
            endpoint,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def get_json(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a GET request and parse the response body as JSON.

        Raises:
            ValueError: If the response is not valid JSON.
        """
        response = self.get(endpoint, params=params, timeout=timeout, **kwargs)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as err:
            preview = response.text[:200]
            raise ValueError(
                f"Expected JSON from {response.url} (status {response.status_code}), "
                f"received non-JSON body: {preview!r}"
            ) from err

    def close(self) -> None:
        """Close the underlying session if owned by this client."""
        if self._owned_session:
            self.session.close()

    def __enter__(self) -> APIClient:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<Test Pilot APIClient(base_url={self.base_url!r}, timeout={self.default_timeout})>"
