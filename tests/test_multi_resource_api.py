"""Test Pilot — Parameterized Multi-Resource REST API Test Suite.

Executes cross-cutting tests across multiple primary resources and relational
sub-resources supported by JSONPlaceholder.
"""

from __future__ import annotations

import pytest

from src.api_client import APIClient
from src.validators import (
    validate_content_type,
    validate_response_time,
    validate_status_code,
)


@pytest.mark.smoke
@pytest.mark.parametrize(
    ("resource", "expected_min_count"),
    [
        ("posts", 100),
        ("users", 10),
        ("comments", 500),
        ("todos", 200),
        ("albums", 100),
    ],
    ids=["posts_catalog", "users_catalog", "comments_catalog", "todos_catalog", "albums_catalog"],
)
def test_resource_listing_and_counts(
    api_client: APIClient,
    resource: str,
    expected_min_count: int,
) -> None:
    """Verify primary REST resources respond with 200 OK and expected record volume."""
    response = api_client.get(f"/{resource}")

    validate_status_code(response, 200)
    validate_content_type(response, "application/json")
    validate_response_time(response, max_duration_seconds=5.0)

    items = response.json()
    assert isinstance(items, list), f"Expected list from /{resource}, got {type(items)}"
    assert len(items) >= expected_min_count, (
        f"Resource /{resource} returned {len(items)} items, expected >= {expected_min_count}"
    )


@pytest.mark.parametrize(
    ("nested_path", "foreign_key", "expected_id"),
    [
        ("/posts/1/comments", "postId", 1),
        ("/posts/2/comments", "postId", 2),
        ("/users/1/posts", "userId", 1),
        ("/users/1/todos", "userId", 1),
        ("/users/1/albums", "userId", 1),
    ],
    ids=[
        "post_1_comments",
        "post_2_comments",
        "user_1_posts",
        "user_1_todos",
        "user_1_albums",
    ],
)
def test_nested_relational_endpoints(
    api_client: APIClient,
    nested_path: str,
    foreign_key: str,
    expected_id: int,
) -> None:
    """Verify nested resource hierarchy correctly filters by parent resource ID."""
    response = api_client.get(nested_path)

    validate_status_code(response, 200)
    validate_content_type(response, "application/json")

    records = response.json()
    assert isinstance(records, list), f"Expected list response from {nested_path}"
    assert len(records) > 0, f"Expected non-empty results from {nested_path}"

    for record in records:
        assert record[foreign_key] == expected_id, (
            f"Record in {nested_path} failed foreign key assertion: "
            f"expected {foreign_key}={expected_id}, got {record.get(foreign_key)}"
        )


@pytest.mark.parametrize("limit", [1, 5, 10, 25])
def test_query_parameter_pagination_limits(
    api_client: APIClient,
    limit: int,
) -> None:
    """Verify JSONPlaceholder supports _limit query parameter to control response size."""
    response = api_client.get("/posts", params={"_limit": limit})

    validate_status_code(response, 200)
    items = response.json()
    assert len(items) == limit, (
        f"Expected exactly {limit} items with _limit={limit}, got {len(items)}"
    )
