"""Strategem Core - Mechanical Primitives Only

This module contains ONLY mechanical primitives used across versions.
No analytical types, no framework-specific concepts, no decision semantics.

Allowed:
- Enums for confidence, execution status, etc.
- Stringly-typed identifiers
- UUIDs, timestamps
- JSON schema helpers

Forbidden:
- Decision, Option, Pressure, Risk (analytical types)
- AnalyticalClaim, StructuralAsymmetry (framework types)
- Any Porter-specific or Strategem-specific types
"""

from enum import Enum
from typing import Literal, Any
from uuid import UUID, uuid4
from datetime import datetime


class ConfidenceLevel(str, Enum):
    """Mechanical confidence level only (no analytical semantics)"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FrameworkName(str):
    """Stringly-typed framework identifier (no enforcement)"""

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return self.value


class ExecutionStatus(str, Enum):
    """Mechanical execution status only"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    INSUFFICIENT = "insufficient"


class ContentType(str, Enum):
    """Mechanical content type identifiers"""

    TEXT = "text"
    DOCUMENT = "document"
    DATA = "data"
    JSON = "json"
    MARKDOWN = "markdown"


def generate_id() -> str:
    """Generate unique identifier (mechanical only)"""
    return str(uuid4())


def get_timestamp() -> datetime:
    """Get current timestamp (mechanical only)"""
    return datetime.now()


def create_uuid() -> UUID:
    """Create UUID object (mechanical only)"""
    return uuid4()


def validate_json_structure(data: Any, required_keys: list[str]) -> bool:
    """Validate JSON has required structure (mechanical only)"""
    if not isinstance(data, dict):
        return False

    for key in required_keys:
        if key not in data:
            return False

    return True


# Version identifiers
V1_VERSION = "1.0.0"
V2_VERSION = "2.0.0-dev"
