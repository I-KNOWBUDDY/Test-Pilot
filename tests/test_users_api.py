"""Test Pilot — Test Suite for /users Resource.

Validates user retrieval, nested object parsing (address, company),
and query filtering by username and email.
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
def test_get_all_users(api_client: APIClient) -> None:
    """Verify GET /users returns the registered users list with 200 OK."""
    response = api_client.get("/users")

    validate_status_code(response, 200)
    validate_content_type(response, "application/json")
    validate_response_time(response, max_duration_seconds=5.0)

    users = response.json()
    assert isinstance(users, list), f"Expected list of users, got {type(users)}"
    assert len(users) == 10, f"Expected 10 default demo users, received {len(users)}"


@pytest.mark.smoke
def test_get_single_user_by_id(api_client: APIClient) -> None:
    """Verify GET /users/1 returns the first user with nested address and company details."""
    response = api_client.get("/users/1")

    validate_status_code(response, 200)
    user = response.json()

    assert user["id"] == 1
    assert user["name"] == "Leanne Graham"
    assert user["username"] == "Bret"
    assert "address" in user and isinstance(user["address"], dict)
    assert "company" in user and isinstance(user["company"], dict)
    assert user["address"]["city"] == "Gwenborough"
    assert "lat" in user["address"]["geo"]


def test_filter_user_by_username(api_client: APIClient) -> None:
    """Verify GET /users?username=Bret retrieves the unique matching account."""
    target_username = "Bret"
    response = api_client.get("/users", params={"username": target_username})

    validate_status_code(response, 200)
    users = response.json()
    assert len(users) == 1, f"Expected 1 user with username {target_username}, found {len(users)}"
    assert users[0]["username"] == target_username
    assert users[0]["id"] == 1


def test_filter_user_by_email(api_client: APIClient) -> None:
    """Verify GET /users?email=Sincere@april.biz correctly matches user record."""
    target_email = "Sincere@april.biz"
    response = api_client.get("/users", params={"email": target_email})

    validate_status_code(response, 200)
    users = response.json()
    assert len(users) == 1, f"Expected 1 user for email {target_email}, got {len(users)}"
    assert users[0]["email"] == target_email
    assert users[0]["name"] == "Leanne Graham"
