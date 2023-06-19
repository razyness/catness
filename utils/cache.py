import functools
import asyncio
from datetime import datetime, timedelta
from collections import OrderedDict


class CacheEntry:
    def __init__(self, result, expiration_time):
        self.result = result
        self.expiration_time = expiration_time


def cache(expiration_time=None, invalidation_interval=None, max_size=None):
    """
    An improved caching decorator for asynchronous functions.

    Args:
        expiration_time (int or timedelta): Optional. The time in seconds or
            timedelta object after which the cache will expire.
            If not provided, the cache will be valid indefinitely.

        invalidation_interval (int or timedelta): Optional. The time in seconds
            or timedelta object at which the cache should be invalidated and updated.
            If not provided, the cache will not be automatically invalidated.

        max_size (int): Optional. The maximum number of entries to store in the cache.
            If the cache exceeds this size, the least recently used item will be evicted.

    Returns:
        coroutine function: The decorated asynchronous function.
    """
    cache_dict = OrderedDict()

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = (func.__name__, _hashable_args(args), _hashable_kwargs(kwargs))

            if key in cache_dict:
                cache_entry = cache_dict[key]
                if expiration_time is None or cache_entry.expiration_time > datetime.now():
                    return cache_entry.result
                else:
                    del cache_dict[key]

            result = await func(*args, **kwargs)
            expiration = _get_expiration_time(expiration_time)
            cache_dict[key] = CacheEntry(result, expiration)

            if max_size is not None and len(cache_dict) > max_size:
                cache_dict.popitem(last=False)

            return result

        async def cache_invalidation_task():
            while True:
                await asyncio.sleep(_get_seconds(invalidation_interval))
                cache_dict.clear()

        if invalidation_interval is not None:
            asyncio.ensure_future(cache_invalidation_task())

        return wrapper

    return decorator


def _hashable_args(args):
    return tuple(_hashable(item) for item in args)


def _hashable_kwargs(kwargs):
    return frozenset((key, _hashable(value)) for key, value in kwargs.items())


def _hashable(item):
    if isinstance(item, dict):
        return _hashable_kwargs(item)
    return item


def _get_expiration_time(duration):
    if duration is None:
        return None
    if isinstance(duration, timedelta):
        return datetime.now() + duration
    if isinstance(duration, int):
        return datetime.now() + timedelta(seconds=duration)
    raise ValueError("Invalid duration format. Please provide an int or timedelta.")


def _get_seconds(duration):
    if duration is None:
        return None
    if isinstance(duration, timedelta):
        return duration.total_seconds()
    if isinstance(duration, int):
        return duration
    raise ValueError("Invalid duration format. Please provide an int or timedelta.")
