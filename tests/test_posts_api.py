"""Test Pilot — Test Suite for /posts Resource.

Validates CRUD operations, query parameter filtering, response headers,
and payload integrity against JSONPlaceholder endpoints.
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
def test_get_all_posts(api_client: APIClient) -> None:
    """Verify GET /posts retrieves the full catalog with 200 OK and expected structure."""
    response = api_client.get("/posts")

    validate_status_code(response, 200)
    validate_content_type(response, "application/json")
    validate_response_time(response, max_duration_seconds=5.0)

    posts = response.json()
    assert isinstance(posts, list), f"Expected list of posts, got {type(posts)}"
    assert len(posts) >= 100, f"Expected at least 100 posts, received {len(posts)}"


@pytest.mark.smoke
def test_get_single_post_by_id(api_client: APIClient) -> None:
    """Verify GET /posts/1 retrieves the designated post accurately."""
    response = api_client.get("/posts/1")

    validate_status_code(response, 200)
    validate_content_type(response, "application/json")

    post = response.json()
    assert post["id"] == 1
    assert post["userId"] == 1
    assert isinstance(post["title"], str) and len(post["title"]) > 0
    assert isinstance(post["body"], str) and len(post["body"]) > 0


@pytest.mark.smoke
def test_create_post(api_client: APIClient) -> None:
    """Verify POST /posts creates a new resource and returns 201 Created with assigned ID."""
    payload = {
        "title": "Test Pilot Automation Post",
        "body": "Validation execution through Test Pilot API testing framework.",
        "userId": 42,
    }
    response = api_client.post("/posts", json=payload)

    validate_status_code(response, 201)
    validate_content_type(response, "application/json")

    created = response.json()
    assert created["id"] == 101, f"Expected simulated ID 101, got {created.get('id')}"
    assert created["title"] == payload["title"]
    assert created["body"] == payload["body"]
    assert created["userId"] == payload["userId"]


def test_update_post_put(api_client: APIClient) -> None:
    """Verify PUT /posts/1 fully updates the resource and returns 200 OK."""
    payload = {
        "id": 1,
        "title": "Test Pilot Fully Replaced Title",
        "body": "Test Pilot Fully Replaced Body Content",
        "userId": 1,
    }
    response = api_client.put("/posts/1", json=payload)

    validate_status_code(response, 200)
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]


def test_partial_update_post_patch(api_client: APIClient) -> None:
    """Verify PATCH /posts/1 partially modifies specific fields and returns 200 OK."""
    patch_payload = {"title": "Test Pilot Patched Title Only"}
    response = api_client.patch("/posts/1", json=patch_payload)

    validate_status_code(response, 200)
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == patch_payload["title"]
    assert "body" in data, "Body field should remain present after partial patch"


def test_delete_post(api_client: APIClient) -> None:
    """Verify DELETE /posts/1 removes resource and returns 200 OK."""
    response = api_client.delete("/posts/1")

    validate_status_code(response, 200)


def test_filter_posts_by_user_id(api_client: APIClient) -> None:
    """Verify GET /posts?userId=2 returns only posts authored by user 2."""
    target_user_id = 2
    response = api_client.get("/posts", params={"userId": target_user_id})

    validate_status_code(response, 200)
    posts = response.json()
    assert len(posts) > 0, f"Expected non-empty posts for user {target_user_id}"
    for post in posts:
        assert post["userId"] == target_user_id, (
            f"Expected userId {target_user_id}, found post with userId {post['userId']}"
        )
