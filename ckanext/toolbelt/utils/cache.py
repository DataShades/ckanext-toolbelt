import pickle
import json

from functools import wraps
from typing import Any, Callable, Generic, Optional, TypeVar, Union, cast

import ckan.lib.redis as redis

from . import constantly

T = TypeVar("T")


class DontCache(Generic[T]):
    __slots__ = ("value",)
    value: T

    def __init__(self, value: T):
        self.value = value

    def unwrap(self) -> T:
        return self.value


MaybeNotCached = Union[T, DontCache[T]]
CacheAwareCallable = Callable[..., MaybeNotCached[T]]
NaiveCallable = Callable[..., T]

CacheDecorator = Callable[[CacheAwareCallable[T]], NaiveCallable[T]]

Duration = Optional[int]
DurationStrategy = Callable[..., Duration]

KeyStr = Union[str, bytes]
KeyStrategy = Callable[..., KeyStr]

Dumper = Callable[[T], KeyStr]
Loader = Callable[[KeyStr], T]


def default_key_strategy(func, *args, **kwargs) -> bytes:
    return bytes(f"{func.__module__}:{func.__name__}", "utf8") + pickle.dumps(
        (args, kwargs)
    )


def decorate_key_strategy(prefix: bytes) -> KeyStrategy:
    def strategy(*args, **kwargs):
        return prefix + default_key_strategy(*args, **kwargs)

    return strategy


class Cache(Generic[T]):
    duration: DurationStrategy
    key: KeyStrategy
    conn: redis.Redis
    dumper: Dumper[T]
    loader: Loader[T]

    def __init__(
        self,
        duration: Union[DurationStrategy, Duration] = None,
        key: Union[KeyStrategy, KeyStr] = default_key_strategy,
        dumper: Dumper[T] = json.dumps,
        loader: Loader[T] = json.loads,
    ):
        self.dumper = dumper
        self.loader = loader

        if not callable(duration):
            duration = constantly(duration)
        self.duration = duration
        if not callable(key):
            key = constantly(key)
        self.key = key

        self.conn = redis.connect_to_redis()

    def __call__(self, func: CacheAwareCallable[T]) -> NaiveCallable[T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            key = self.key(func, *args, **kwargs)
            old_value = self.conn.get(key)

            if old_value:
                return self.loader(old_value)

            value = func(*args, **kwargs)
            if isinstance(value, DontCache):
                return cast(T, value.unwrap())

            duration = self.duration(func, *args, **kwargs)
            self.conn.set(key, self.dumper(value), ex=duration)
            return value

        def reset(*args: Any, **kwargs: Any) -> int:
            key = self.key(func, *args, **kwargs)
            return self.conn.delete(key)

        wrapper.reset = reset

        return wrapper
