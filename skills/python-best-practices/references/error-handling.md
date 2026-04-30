# Python Error Handling Reference

Use this reference when reviewing or writing validation logic, exceptions, and failure-handling behavior in Python services, scripts, and libraries.

## Core Principles

- Validate early.
- Use specific exception types.
- Preserve error context.
- Model partial failures instead of hiding them.

## Early Input Validation

Validate inputs at the boundary, before expensive work begins.

```python
def process_order(
    order_id: str,
    quantity: int,
    discount_percent: float,
) -> OrderResult:
    if not order_id:
        raise ValueError("'order_id' is required")

    if quantity <= 0:
        raise ValueError(f"'quantity' must be positive, got {quantity}")

    if not 0 <= discount_percent <= 100:
        raise ValueError(
            f"'discount_percent' must be 0-100, got {discount_percent}"
        )

    return _process_validated_order(order_id, quantity, discount_percent)
```

## Convert To Domain Types At Boundaries

Parse raw strings and untrusted data into typed domain values early.

```python
from enum import Enum


class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"


def parse_output_format(value: str) -> OutputFormat:
    try:
        return OutputFormat(value.lower())
    except ValueError as exc:
        valid_formats = [fmt.value for fmt in OutputFormat]
        raise ValueError(
            f"Invalid format '{value}'. Valid options: {', '.join(valid_formats)}"
        ) from exc
```

## Pydantic For Structured Validation

For complex request bodies or config, use Pydantic to validate and normalize data consistently.

```python
from pydantic import BaseModel, Field, ValidationError, field_validator


class CreateUserInput(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format")
        return value.lower()

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().title()
```

## Use Standard Exceptions Intentionally

Map common failures to familiar built-in exceptions where possible:

- `ValueError` for invalid values
- `TypeError` for wrong input types
- `KeyError` for missing keys
- `RuntimeError` for operational failures
- `TimeoutError` for timeouts
- `FileNotFoundError` for missing paths
- `PermissionError` for access failures

Avoid vague `Exception("something went wrong")` style errors.

## Custom Exception Hierarchies

Create domain-specific exceptions when the caller needs structured semantics.

```python
class ApiError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class RateLimitError(ApiError):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after}s",
            status_code=429,
        )
```

## Exception Chaining

Preserve the original failure when translating exceptions across layers.

```python
import httpx


class ServiceError(Exception):
    pass


def upload_file(path: str) -> str:
    try:
        with open(path, "rb") as handle:
            response = httpx.post("https://upload.example.com", files={"file": handle})
            response.raise_for_status()
            return response.json()["url"]
    except FileNotFoundError as exc:
        raise ServiceError(f"Upload failed: file not found at '{path}'") from exc
    except httpx.HTTPStatusError as exc:
        raise ServiceError(
            f"Upload failed: server returned {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise ServiceError("Upload failed: network error") from exc
```

## Batch Processing With Partial Failures

One bad item should not automatically abort a whole batch unless the product requirement says so.

```python
from dataclasses import dataclass


@dataclass
class BatchResult[T]:
    succeeded: dict[int, T]
    failed: dict[int, Exception]

    @property
    def success_count(self) -> int:
        return len(self.succeeded)

    @property
    def failure_count(self) -> int:
        return len(self.failed)


def process_batch(items: list[Item]) -> BatchResult[ProcessedItem]:
    succeeded: dict[int, ProcessedItem] = {}
    failed: dict[int, Exception] = {}

    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process_single_item(item)
        except Exception as exc:
            failed[idx] = exc

    return BatchResult(succeeded=succeeded, failed=failed)
```

If failures are user-visible or operationally meaningful, surface counts, identities, and reasons clearly.

## Progress Reporting For Long Operations

Long-running batch work often needs progress updates without coupling domain logic to UI code.

```python
from collections.abc import Callable


ProgressCallback = Callable[[int, int, str], None]


def process_large_batch(
    items: list[Item],
    on_progress: ProgressCallback | None = None,
) -> BatchResult:
    total = len(items)
    succeeded = {}
    failed = {}

    for idx, item in enumerate(items):
        if on_progress:
            on_progress(idx, total, f"Processing {item.id}")

        try:
            succeeded[idx] = process_single_item(item)
        except Exception as exc:
            failed[idx] = exc

    if on_progress:
        on_progress(total, total, "Complete")

    return BatchResult(succeeded=succeeded, failed=failed)
```

## Error-Handling Checklist

- Inputs are validated at boundaries
- Raw data is converted to domain types early
- Pydantic or equivalent validation is used for structured payloads where helpful
- Exceptions are specific and include actionable context
- Lower-level exceptions are chained when translated
- Batch operations model partial success and failure explicitly
- Long operations can report progress without tangling UI with business logic
- Tests cover failure paths, not just successful execution
