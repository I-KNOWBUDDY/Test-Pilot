"""Test Pilot — Response and Schema Validation Utilities.

Provides assertion helpers with diagnostic error reporting for status codes,
JSON schemas, content types, and latency thresholds.
"""

from __future__ import annotations

from typing import Any

import jsonschema
import requests


def validate_status_code(
    response: requests.Response,
    expected_status: int | tuple[int, ...] | list[int],
) -> None:
    """Validate that the HTTP response status code matches expected value(s).

    Produces clear diagnostic output including the request method, target URL,
    and a preview of the response body upon mismatch.

    Args:
        response: The requests.Response object to validate.
        expected_status: Expected HTTP status code or tuple/list of allowed status codes.

    Raises:
        AssertionError: If response.status_code does not match expected_status.
    """
    actual = response.status_code
    if isinstance(expected_status, (tuple, list)):
        if actual not in expected_status:
            body_preview = response.text[:250].strip() or "<empty body>"
            raise AssertionError(
                f"Status code mismatch for {response.request.method} {response.url}!\n"
                f"  Expected one of: {list(expected_status)}\n"
                f"  Actual status:   {actual}\n"
                f"  Response preview: {body_preview}"
            )
    else:
        if actual != expected_status:
            body_preview = response.text[:250].strip() or "<empty body>"
            raise AssertionError(
                f"Status code mismatch for {response.request.method} {response.url}!\n"
                f"  Expected status: {expected_status}\n"
                f"  Actual status:   {actual}\n"
                f"  Response preview: {body_preview}"
            )


def validate_json_schema(
    instance: Any,
    schema: dict[str, Any],
    schema_name: str = "JSON Schema",
) -> None:
    """Validate a Python dictionary/list against a JSON Schema.

    On validation failure, aggregates schema error details into a structured,
    human-readable message highlighting the exact property path and issue.

    Args:
        instance: The parsed JSON data to validate.
        schema: The JSON Schema definition.
        schema_name: A descriptive label for the schema in failure messages.

    Raises:
        AssertionError: If validation against the schema fails.
    """
    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: str(e.path))

    if errors:
        error_details: list[str] = []
        for idx, error in enumerate(errors[:5], start=1):
            path = ".".join(str(p) for p in error.path) or "<root>"
            error_details.append(
                f"  [{idx}] Path: '{path}' -> {error.message} (value: {error.instance!r})"
            )
        total = len(errors)
        overflow = f"\n  ... and {total - 5} more error(s)" if total > 5 else ""
        raise AssertionError(
            f"Contract validation failed against '{schema_name}' ({total} violation(s)):\n"
            + "\n".join(error_details)
            + overflow
        )


def validate_content_type(
    response: requests.Response,
    expected_content_type: str = "application/json",
) -> None:
    """Validate that the response Content-Type header matches or contains the expected MIME type.

    Args:
        response: The requests.Response object to check.
        expected_content_type: Expected MIME type substring (e.g. 'application/json').

    Raises:
        AssertionError: If the Content-Type header is missing or does not match.
    """
    content_type = response.headers.get("Content-Type", "")
    if expected_content_type.lower() not in content_type.lower():
        raise AssertionError(
            f"Content-Type mismatch for {response.request.method} {response.url}!\n"
            f"  Expected header to contain: {expected_content_type!r}\n"
            f"  Actual Content-Type:         {content_type!r}"
        )


def validate_response_time(
    response: requests.Response,
    max_duration_seconds: float = 5.0,
) -> None:
    """Validate that the response elapsed time is within an acceptable threshold.

    Args:
        response: The requests.Response object to check.
        max_duration_seconds: Maximum allowed elapsed time in seconds.

    Raises:
        AssertionError: If elapsed time exceeds the threshold.
    """
    elapsed = response.elapsed.total_seconds()
    if elapsed > max_duration_seconds:
        raise AssertionError(
            f"Response time SLA exceeded for {response.request.method} {response.url}!\n"
            f"  Maximum allowed: {max_duration_seconds:.2f}s\n"
            f"  Actual duration: {elapsed:.2f}s"
        )
