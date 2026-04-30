# Python Performance Reference

Use this reference when Python code is slow, memory-heavy, async-sensitive, or likely to sit on a hot path. Profile first, then optimize the measured bottleneck.

## Profiling Tools

### `cProfile` For CPU Profiling

```python
import cProfile
import pstats
from pstats import SortKey


def slow_function():
    total = 0
    for i in range(1_000_000):
        total += i
    return total


def another_function():
    return [i**2 for i in range(100_000)]


def main():
    result1 = slow_function()
    result2 = another_function()
    return result1, result2


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)
    stats.dump_stats("profile_output.prof")
```

Command-line usage:

```bash
python -m cProfile -o output.prof script.py
python -m pstats output.prof
```

### `line_profiler` For Line-Level Hotspots

```python
@profile
def process_data(data):
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result
```

Run with `kernprof -l -v script.py`.

### `memory_profiler` For Allocation Pressure

```python
from memory_profiler import profile


@profile
def memory_intensive():
    big_list = [i for i in range(1_000_000)]
    big_dict = {i: i**2 for i in range(100_000)}
    return sum(big_list)
```

Run with `python -m memory_profiler script.py`.

### `py-spy` For Production-Safe Sampling

```bash
py-spy top --pid 12345
py-spy record -o profile.svg --pid 12345
py-spy record -o profile.svg -- python script.py
py-spy dump --pid 12345
```

## Optimization Patterns

### Prefer Comprehensions Over Manual Append Loops

```python
def slow_squares(n):
    result = []
    for i in range(n):
        result.append(i**2)
    return result


def fast_squares(n):
    return [i**2 for i in range(n)]
```

### Prefer Generators For Large Streaming Work

```python
def list_approach():
    data = [i**2 for i in range(1_000_000)]
    return sum(data)


def generator_approach():
    data = (i**2 for i in range(1_000_000))
    return sum(data)
```

Generators reduce peak memory when you do not need the entire intermediate collection.

### Use `"".join(...)` For Repeated String Building

```python
def slow_concat(items):
    result = ""
    for item in items:
        result += str(item)
    return result


def fast_concat(items):
    return "".join(str(item) for item in items)
```

### Prefer Dict And Set Lookups Over Repeated Linear Searches

```python
items = list(range(10_000))
lookup_dict = {i: i for i in range(10_000)}


def list_search(target):
    return target in items


def dict_search(target):
    return target in lookup_dict
```

Use the right data structure before reaching for micro-optimizations.

### Keep Hot Values Local On Tight Loops

```python
GLOBAL_VALUE = 100


def use_global():
    total = 0
    for _ in range(10_000):
        total += GLOBAL_VALUE
    return total


def use_local():
    local_value = 100
    total = 0
    for _ in range(10_000):
        total += local_value
    return total
```

This is a minor optimization, but it can matter inside very hot loops after higher-value issues are resolved.

## Async Performance Trap

One of the highest-impact Python performance mistakes is putting blocking work inside `async def` code.

```python
# BAD: blocks the event loop and stalls unrelated work
async def fetch_data():
    time.sleep(1)
    response = requests.get(url)
    return response.json()
```

Use async-native clients, awaitable sleeps, or offload blocking work intentionally.

```python
# GOOD
async def fetch_data():
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

Also watch for hidden blockers inside async flows:

- synchronous ORM calls
- heavy CPU work in request handlers
- filesystem work in tight async request paths
- libraries that expose async wrappers but still block internally

## Review Guidance

- Measure before changing algorithms or structure.
- Focus on hot paths, large collections, repeated I/O, and repeated allocations.
- Prefer built-in operations and standard-library primitives before custom cleverness.
- Check algorithmic complexity before micro-tuning syntax.
- Treat memory pressure and latency as separate concerns; a fix for one can hurt the other.
- In async code, verify that the full path is non-blocking, not just the top-level function signature.

## Performance Checklist

- Profile with `cProfile`, `line_profiler`, `memory_profiler`, or `py-spy`
- Optimize the measured bottleneck, not guessed bottlenecks
- Prefer comprehensions, generators, and appropriate data structures
- Avoid repeated string concatenation in loops
- Reduce unnecessary copies and redundant work
- Avoid blocking calls inside `async def`
- Re-check performance after each meaningful change
