"""Test Pilot — Negative and Boundary Test Cases.

Validates error handling for non-existent entities, malformed identifiers,
unknown paths, empty query matches, and timeout enforcement.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from src.api_client import APIClient
from src.validators import validate_status_code


@pytest.mark.parametrize(
    "invalid_endpoint",
    [
        "/posts/999999",
        "/users/999999",
        "/comments/999999",
        "/todos/999999",
        "/posts/-1",
        "/posts/invalid-alphanumeric-id",
        "/completely_nonexistent_route_abc123",
    ],
    ids=[
        "nonexistent_post",
        "nonexistent_user",
        "nonexistent_comment",
        "nonexistent_todo",
        "negative_post_id",
        "string_id_on_numeric_route",
        "unknown_route",
    ],
)
def test_nonexistent_resources_return_404(
    api_client: APIClient,
    invalid_endpoint: str,
) -> None:
    """Verify that requests to non-existent or invalid endpoints return HTTP 404 Not Found."""
    response = api_client.get(invalid_endpoint)
    validate_status_code(response, 404)


@pytest.mark.parametrize(
    ("endpoint", "filter_params"),
    [
        ("/posts", {"userId": 999999}),
        ("/users", {"username": "ghost_user_that_does_not_exist_404"}),
        ("/comments", {"postId": 999999}),
    ],
    ids=[
        "posts_for_nonexistent_user",
        "users_for_nonexistent_username",
        "comments_for_nonexistent_post",
    ],
)
def test_queries_with_unknown_identifiers_return_empty_list(
    api_client: APIClient,
    endpoint: str,
    filter_params: dict[str, object],
) -> None:
    """Verify unknown filter identifiers succeed with HTTP 200 and return empty list []."""
    response = api_client.get(endpoint, params=filter_params)
    validate_status_code(response, 200)

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0, f"Expected empty array for params {filter_params}, received {data}"


def test_client_enforces_explicit_timeout(base_url: str) -> None:
    """Verify APIClient explicitly enforces timeouts and propagates Timeout exceptions."""
    mock_session = MagicMock(spec=requests.Session)
    mock_session.request.side_effect = requests.exceptions.Timeout("Request timed out")

    client = APIClient(base_url=base_url, session=mock_session, default_timeout=5.0)

    # 1. Custom timeout parameter is explicitly forwarded and Timeout exception is propagated
    with pytest.raises(requests.exceptions.Timeout):
        client.get("/posts", timeout=2.5)

    mock_session.request.assert_called_with(
        method="GET",
        url=f"{base_url.rstrip('/')}/posts",
        timeout=2.5,
        params=None,
        headers=None,
    )

    # 2. Default timeout is explicitly enforced when no per-request timeout is provided
    with pytest.raises(requests.exceptions.Timeout):
        client.get("/posts")

    mock_session.request.assert_called_with(
        method="GET",
        url=f"{base_url.rstrip('/')}/posts",
        timeout=5.0,
        params=None,
        headers=None,
    )


def test_validate_status_code_raises_informative_assertion_error(api_client: APIClient) -> None:
    """Verify validate_status_code raises an AssertionError with diagnostics upon mismatch."""
    response = api_client.get("/posts/1")
    with pytest.raises(AssertionError) as exc_info:
        validate_status_code(response, expected_status=404)

    error_msg = str(exc_info.value)
    assert "Expected status: 404" in error_msg
    assert "Actual status:   200" in error_msg
    assert "GET" in error_msg
