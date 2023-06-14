import functools
import asyncio
from datetime import datetime, timedelta


def cache(expiration_time=None, invalidation_interval=None):
    """
    A general-purpose caching decorator for asynchronous functions.

    Args:
        expiration_time (int or timedelta): Optional. The time in seconds or
            timedelta object after which the cache will expire.
            If not provided, the cache will be valid indefinitely.

        invalidation_interval (int or timedelta): Optional. The time in seconds
            or timedelta object at which the cache should be invalidated and updated.
            If not provided, the cache will not be automatically invalidated.

    Returns:
        coroutine function: The decorated asynchronous function.
    """
    memo = {}

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = (func.__name__, args, frozenset(kwargs.items()))

            if key in memo:
                if expiration_time is None or memo[key][0] > datetime.now():
                    return memo[key][1]
                else:
                    del memo[key]

            result = await func(*args, **kwargs)
            memo[key] = (datetime.now() + _get_timedelta(expiration_time), result)
            return result

        async def cache_invalidation_task():
            while True:
                await asyncio.sleep(_get_seconds(invalidation_interval))
                memo.clear()

        if invalidation_interval is not None:
            asyncio.ensure_future(cache_invalidation_task())

        return wrapper

    return decorator

def _get_timedelta(duration):
    if isinstance(duration, timedelta):
        return duration
    elif isinstance(duration, int):
        return timedelta(seconds=duration)
    else:
        raise ValueError("Invalid duration format. Please provide an int or timedelta.")

def _get_seconds(duration):
    if isinstance(duration, timedelta):
        return duration.total_seconds()
    elif isinstance(duration, int):
        return duration
    else:
        raise ValueError("Invalid duration format. Please provide an int or timedelta.")
