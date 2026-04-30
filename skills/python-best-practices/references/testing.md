# Python Testing Reference

Use this reference when reviewing or writing Python tests, especially with pytest. Focus on clarity, isolation, realistic boundaries, and coverage of failure modes.

## Core Test Design

### AAA Pattern

Structure tests around arrange, act, and assert so failures are easier to read and maintain.

```python
def test_add():
    result = add(2, 3)
    assert result == 5
```

### One Behavior Per Test

```python
# BAD
def test_user_service():
    user = service.create_user(data)
    assert user.id is not None
    assert user.email == data["email"]
    updated = service.update_user(user.id, {"name": "New"})
    assert updated.name == "New"
```

```python
# GOOD
def test_create_user_assigns_id():
    user = service.create_user(data)
    assert user.id is not None


def test_create_user_stores_email():
    user = service.create_user(data)
    assert user.email == data["email"]


def test_update_user_changes_name():
    user = service.create_user(data)
    updated = service.update_user(user.id, {"name": "New"})
    assert updated.name == "New"
```

### Test Error Paths

```python
def test_get_user_raises_not_found():
    with pytest.raises(UserNotFoundError) as exc_info:
        service.get_user("nonexistent-id")

    assert "nonexistent-id" in str(exc_info.value)
```

## Pytest Fundamentals

### Fixtures

Use fixtures for setup and teardown so test data creation is reusable and explicit.

```python
import pytest
from typing import Generator


class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def query(self, sql: str) -> list:
        if not self.connected:
            raise RuntimeError("Not connected")
        return [{"id": 1, "name": "Test"}]


@pytest.fixture
def db() -> Generator[Database, None, None]:
    database = Database("sqlite:///:memory:")
    database.connect()
    yield database
    database.disconnect()
```

Prefer the narrowest fixture scope that keeps tests fast enough and isolated enough.

### Parameterization

```python
@pytest.mark.parametrize(
    "email,expected",
    [
        ("user@example.com", True),
        ("test.user@domain.co.uk", True),
        ("invalid.email", False),
        ("@example.com", False),
        ("user@domain", False),
        ("", False),
    ],
)
def test_email_validation(email, expected):
    assert is_valid_email(email) == expected
```

Parameterization is usually better than copy-pasting multiple nearly identical tests.

### Markers

```python
@pytest.mark.slow
def test_slow_operation():
    ...


@pytest.mark.integration
def test_database_integration():
    ...
```

Use markers to separate slow, integration, platform-specific, or expected-failure cases.

## Mocking With `unittest.mock`

Mock external boundaries such as HTTP calls, queues, and third-party services. Avoid mocking every internal collaborator unless isolation truly requires it.

```python
from unittest.mock import Mock, patch


def test_get_user_success():
    client = APIClient("https://api.example.com")

    mock_response = Mock()
    mock_response.json.return_value = {"id": 1, "name": "John Doe"}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        user = client.get_user(1)

        assert user["id"] == 1
        mock_get.assert_called_once_with("https://api.example.com/users/1")
```

For retry logic, use side effects to model transient and permanent failures.

```python
def test_retries_on_transient_error():
    client = Mock()
    client.request.side_effect = [
        ConnectionError("Failed"),
        ConnectionError("Failed"),
        {"status": "ok"},
    ]

    service = ServiceWithRetry(client, max_retries=3)
    result = service.fetch()

    assert result == {"status": "ok"}
    assert client.request.call_count == 3
```

## Exception Testing

```python
def test_zero_division_with_message():
    with pytest.raises(ZeroDivisionError, match="Division by zero"):
        divide(5, 0)
```

Assert both the exception type and the meaningful part of the message when the message encodes user-facing or debugging value.

## Time Control

Use `freezegun` or an equivalent tool for time-dependent logic.

```python
from freezegun import freeze_time
from datetime import datetime


@freeze_time("2026-01-15 10:00:00")
def test_token_expiry():
    token = create_token(expires_in_seconds=3600)
    assert token.expires_at == datetime(2026, 1, 15, 11, 0, 0)
```

## Coverage Reporting

Use coverage to identify missing paths, not as the only quality signal.

```bash
pytest --cov=myapp tests/
pytest --cov=myapp --cov-report=html tests/
pytest --cov=myapp --cov-fail-under=80 tests/
pytest --cov=myapp --cov-report=term-missing tests/
```

High percentage coverage with weak assertions or excessive mocking is still weak testing.

## Test Organization

```text
tests/
  conftest.py
  test_unit/
    test_models.py
    test_utils.py
  test_integration/
    test_api.py
    test_database.py
  test_e2e/
    test_workflows.py
```

Shared fixtures belong in `conftest.py`. Keep unit, integration, and end-to-end coverage clearly separated when the suite is large enough to justify it.

## Naming Guidance

A reliable default is `test_<unit>_<scenario>_<expected_outcome>`.

```python
def test_create_user_with_valid_data_returns_user():
    ...


def test_create_user_with_duplicate_email_raises_conflict():
    ...
```

## Testing Checklist

- Tests follow arrange, act, assert clearly enough to read quickly
- Fixtures keep setup reusable without hiding too much behavior
- Parameterization replaces repetitive copy-paste tests
- Mocks are used for real external boundaries, not everything
- Error paths and edge cases are covered
- Retry logic, validation, and exception messages are tested where important
- Time-dependent behavior is controlled deterministically
- Coverage reporting is used to find blind spots
