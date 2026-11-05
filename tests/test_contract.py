"""Test Pilot — Contract and Schema Validation Test Suite.

Ensures that REST responses adhere strictly to JSON Schema (Draft-7) definitions.
Marked with the 'contract' marker for isolated test execution.
"""

from __future__ import annotations

import pytest

from src.api_client import APIClient
from src.validators import (
    validate_content_type,
    validate_json_schema,
    validate_status_code,
)
from tests.schemas import (
    COMMENT_LIST_SCHEMA,
    COMMENT_SCHEMA,
    POST_LIST_SCHEMA,
    POST_SCHEMA,
    TODO_LIST_SCHEMA,
    TODO_SCHEMA,
    USER_LIST_SCHEMA,
    USER_SCHEMA,
)


@pytest.mark.contract
def test_post_contract_single(api_client: APIClient) -> None:
    """Validate that GET /posts/1 conforms to POST_SCHEMA."""
    response = api_client.get("/posts/1")
    validate_status_code(response, 200)
    validate_content_type(response, "application/json")

    validate_json_schema(response.json(), POST_SCHEMA, schema_name="Single Post Schema")


@pytest.mark.contract
def test_post_contract_list(api_client: APIClient) -> None:
    """Validate that GET /posts conforms to POST_LIST_SCHEMA."""
    response = api_client.get("/posts")
    validate_status_code(response, 200)

    validate_json_schema(response.json(), POST_LIST_SCHEMA, schema_name="Post List Schema")


@pytest.mark.contract
def test_user_contract_single(api_client: APIClient) -> None:
    """Validate that GET /users/1 conforms to USER_SCHEMA."""
    response = api_client.get("/users/1")
    validate_status_code(response, 200)

    validate_json_schema(response.json(), USER_SCHEMA, schema_name="Single User Schema")


@pytest.mark.contract
def test_user_contract_list(api_client: APIClient) -> None:
    """Validate that GET /users conforms to USER_LIST_SCHEMA."""
    response = api_client.get("/users")
    validate_status_code(response, 200)

    validate_json_schema(response.json(), USER_LIST_SCHEMA, schema_name="User List Schema")


@pytest.mark.contract
def test_comment_contract_single_and_list(api_client: APIClient) -> None:
    """Validate that GET /comments/1 and /comments conform to their schemas."""
    single_res = api_client.get("/comments/1")
    validate_status_code(single_res, 200)
    validate_json_schema(single_res.json(), COMMENT_SCHEMA, schema_name="Comment Schema")

    list_res = api_client.get("/comments", params={"_limit": 5})
    validate_status_code(list_res, 200)
    validate_json_schema(list_res.json(), COMMENT_LIST_SCHEMA, schema_name="Comment List Schema")


@pytest.mark.contract
def test_todo_contract_single_and_list(api_client: APIClient) -> None:
    """Validate that GET /todos/1 and /todos conform to their schemas."""
    single_res = api_client.get("/todos/1")
    validate_status_code(single_res, 200)
    validate_json_schema(single_res.json(), TODO_SCHEMA, schema_name="Todo Schema")

    list_res = api_client.get("/todos", params={"_limit": 5})
    validate_status_code(list_res, 200)
    validate_json_schema(list_res.json(), TODO_LIST_SCHEMA, schema_name="Todo List Schema")


@pytest.mark.contract
def test_schema_validator_catches_contract_violations() -> None:
    """Verify that validate_json_schema detects schema discrepancies with detailed diagnostics."""
    invalid_post_payload = {
        "id": "not-an-integer",  # violates integer type
        "userId": 1,
        # missing required field "title"
        "body": "Sample body",
    }

    with pytest.raises(AssertionError) as exc_info:
        validate_json_schema(
            invalid_post_payload,
            POST_SCHEMA,
            schema_name="Test Post Contract",
        )

    error_message = str(exc_info.value)
    assert "Contract validation failed against 'Test Post Contract'" in error_message
    assert "violation(s)" in error_message
    # Check that it identifies missing property or type mismatch
    assert "title" in error_message or "not-an-integer" in error_message
