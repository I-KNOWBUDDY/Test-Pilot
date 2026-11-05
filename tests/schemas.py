"""Test Pilot — JSON Schema Definitions for API Contract Testing.

Defines Draft-7 compliant schemas matching standard JSONPlaceholder resources.
"""

from __future__ import annotations

POST_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"},
    },
    "required": ["userId", "id", "title", "body"],
    "additionalProperties": True,
}

POST_LIST_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": POST_SCHEMA,
    "minItems": 1,
}

USER_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "username": {"type": "string"},
        "email": {"type": "string"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "suite": {"type": "string"},
                "city": {"type": "string"},
                "zipcode": {"type": "string"},
                "geo": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "string"},
                        "lng": {"type": "string"},
                    },
                    "required": ["lat", "lng"],
                },
            },
            "required": ["street", "city", "zipcode"],
        },
        "phone": {"type": "string"},
        "website": {"type": "string"},
        "company": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "catchPhrase": {"type": "string"},
                "bs": {"type": "string"},
            },
            "required": ["name"],
        },
    },
    "required": ["id", "name", "username", "email"],
    "additionalProperties": True,
}

USER_LIST_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": USER_SCHEMA,
    "minItems": 1,
}

COMMENT_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "postId": {"type": "integer"},
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string"},
        "body": {"type": "string"},
    },
    "required": ["postId", "id", "name", "email", "body"],
    "additionalProperties": True,
}

COMMENT_LIST_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": COMMENT_SCHEMA,
    "minItems": 1,
}

TODO_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "completed": {"type": "boolean"},
    },
    "required": ["userId", "id", "title", "completed"],
    "additionalProperties": True,
}

TODO_LIST_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": TODO_SCHEMA,
    "minItems": 1,
}
