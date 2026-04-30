# Python Anti-Patterns Reference

Use this reference when reviewing Python code for maintainability, architecture, reliability, and test-quality issues that are easy to miss during implementation.

## Infrastructure Anti-Patterns

### Scattered Timeout And Retry Logic

```python
# BAD: timeout and retry behavior duplicated at call sites
def fetch_user(user_id: str):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("Timeout fetching user")
        return None


def fetch_orders(user_id: str):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("Timeout fetching orders")
        return None
```

Centralize this in one client wrapper, decorator, or service boundary so behavior is consistent and tunable.

```python
# GOOD: one place owns retry and timeout behavior
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def http_get(url: str) -> Response:
    return requests.get(url, timeout=30)
```

### Double Retry

```python
# BAD: retries happen in more than one layer
@retry(max_attempts=3)
def call_service():
    return client.request()
```

Retry in one layer only. If the HTTP client, SDK, queue, or infrastructure already retries, avoid wrapping it in another retry loop unless there is a deliberate policy.

### Hard-Coded Configuration

```python
# BAD: config and secrets live in source code
DB_HOST = "prod-db.example.com"
API_KEY = "sk-12345"


def connect():
    return psycopg.connect(f"host={DB_HOST}...")
```

Move configuration to typed settings and keep secrets out of code.

```python
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    db_host: str = Field(alias="DB_HOST")
    api_key: str = Field(alias="API_KEY")


settings = Settings()
```

## Architecture Smells

### Exposed Internal Types

```python
# BAD: API returns ORM types directly
@app.get("/users/{id}")
def get_user(id: str) -> UserModel:
    return db.query(UserModel).get(id)
```

Keep persistence models, protobufs, and other internal types behind explicit DTOs or response models.

```python
# GOOD
@app.get("/users/{id}")
def get_user(id: str) -> UserResponse:
    user = db.query(UserModel).get(id)
    return UserResponse.model_validate(user)
```

### Mixed I/O And Business Logic

```python
# BAD: queries and rules are tangled together
def calculate_discount(user_id: str) -> float:
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    if len(orders) > 10:
        return 0.15
    return 0.0
```

Push I/O to repositories or adapters. Keep business rules pure when possible.

```python
# GOOD
def calculate_discount(user: User, orders: list[Order]) -> float:
    if len(orders) > 10:
        return 0.15
    return 0.0
```

## Error Handling Mistakes

### Bare Exception Handling

```python
# BAD: hides failures and destroys signal
try:
    process()
except Exception:
    pass
```

Catch specific exceptions and either translate them, log them with context, or re-raise them.

```python
# GOOD
try:
    process()
except ConnectionError as exc:
    logger.warning("Connection failed, will retry", error=str(exc))
    raise
except ValueError as exc:
    logger.error("Invalid input", error=str(exc))
    raise BadRequestError(str(exc))
```

### Ignored Partial Failures

```python
# BAD: one bad item aborts the entire batch
def process_batch(items):
    results = []
    for item in items:
        result = process(item)
        results.append(result)
    return results
```

If a batch can partially succeed, model that explicitly.

```python
# GOOD
def process_batch(items) -> BatchResult:
    succeeded = {}
    failed = {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process(item)
        except Exception as exc:
            failed[idx] = exc
    return BatchResult(succeeded, failed)
```

### Missing Input Validation

```python
# BAD: invalid input fails somewhere deeper and less clearly
def create_user(data: dict):
    return User(**data)
```

Validate at the boundary and fail early with a clear error.

```python
# GOOD
def create_user(data: dict) -> User:
    validated = CreateUserInput.model_validate(data)
    return User.from_input(validated)
```

## Resource Leaks

### Unclosed Resources

```python
# BAD
def read_file(path):
    handle = open(path)
    return handle.read()
```

Use context managers so cleanup happens on both success and failure.

```python
# GOOD
def read_file(path):
    with open(path) as handle:
        return handle.read()
```

### Blocking In Async Code

```python
# BAD: blocks the event loop
async def fetch_data():
    time.sleep(1)
    response = requests.get(url)
```

Use async-native APIs in async code paths.

```python
# GOOD
async def fetch_data():
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
```

## Type Safety Gaps

### Missing Type Hints

```python
# BAD
def process(data):
    return data["value"] * 2
```

Annotate public functions and important internal boundaries.

```python
# GOOD
def process(data: dict[str, int]) -> int:
    return data["value"] * 2
```

### Untyped Collections

```python
# BAD
def get_users() -> list:
    ...
```

Prefer explicit parameterized collection types.

```python
# GOOD
def get_users() -> list[User]:
    ...
```

## Testing Anti-Patterns

### Only Testing Happy Paths

```python
# BAD
def test_create_user():
    user = service.create_user(valid_data)
    assert user.id is not None
```

Cover invalid inputs, edge cases, and behavior under conflict or failure.

```python
# GOOD
def test_create_user_success():
    user = service.create_user(valid_data)
    assert user.id is not None


def test_create_user_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        service.create_user(invalid_email_data)


def test_create_user_duplicate_email():
    service.create_user(valid_data)
    with pytest.raises(ConflictError):
        service.create_user(valid_data)
```

### Over-Mocking

```python
# BAD: the test mostly verifies mocks, not behavior
def test_user_service():
    mock_repo = Mock()
    mock_cache = Mock()
    mock_logger = Mock()
    mock_metrics = Mock()
```

Mock external boundaries, not every collaborator by default. Prefer integration coverage for critical flows.

## Review Checklist

- No scattered retry and timeout logic
- No accidental double retry across layers
- No hard-coded configuration or secrets
- No exposed internal persistence or transport types
- No mixed I/O and business logic where separation would simplify testing
- No bare `except Exception: pass`
- No unmodeled partial failures in batch work
- No missing boundary validation
- No leaked files, sockets, or connections
- No blocking calls in async code paths
- Public functions and collections are typed clearly
- Tests cover error paths, not just happy paths
