import json
import logging
import pickle  # nosec: B403
from functools import update_wrapper
from typing import Any, Callable, Generic, Optional, Protocol, TypeVar, Union, cast

from typing_extensions import ParamSpec

from ckan.lib import redis

from . import constantly

log = logging.getLogger(__name__)
T = TypeVar("T")
TC = TypeVar("TC", covariant=True)
P = ParamSpec("P")


class DontCache(Generic[T]):
    __slots__ = ("value",)
    value: T

    def __init__(self, value: T):
        self.value = value

    def unwrap(self) -> T:
        return self.value


MaybeNotCached = Union[T, DontCache[T]]
CacheAwareCallable = Callable[P, MaybeNotCached[T]]


class NaiveCallable(Generic[P, TC], Protocol):
    def reset(self, *args: P.args, **kwargs: P.kwargs) -> int:
        ...

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> TC:
        ...


CacheDecorator = Callable[[CacheAwareCallable[P, T]], NaiveCallable[P, T]]

Duration = Optional[int]
DurationStrategy = Callable[..., Duration]

KeyStr = Union[str, bytes]
KeyStrategy = Callable[..., KeyStr]

Dumper = Callable[[T], KeyStr]
Loader = Callable[[KeyStr], T]


def default_key_strategy(func: Callable[..., Any], *args: Any, **kwargs: Any) -> bytes:
    return bytes(f"{func.__module__}:{func.__name__}", "utf8") + pickle.dumps(
        (args, kwargs),
    )


def decorate_key_strategy(prefix: bytes, after: bool = False) -> KeyStrategy:
    def strategy(*args: Any, **kwargs: Any):
        left = prefix
        right = default_key_strategy(*args, **kwargs)
        if after:
            left, right = right, left

        return left + right

    return strategy


class Cache(Generic[T]):
    duration: DurationStrategy
    key: KeyStrategy
    conn: "redis.Redis[bytes]"
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

    @staticmethod
    def dont_cache(value: T):
        return DontCache(value)

    def __call__(self, func: CacheAwareCallable[P, T]) -> NaiveCallable[P, T]:
        caller = Caller(func, self)
        return cast(Caller[P, T], update_wrapper(caller, func))


class Caller(NaiveCallable[P, T]):
    def __init__(self, func: CacheAwareCallable[P, T], cache: Cache[T]):
        self.func = func
        self.cache = cache

    def reset(self, *args: P.args, **kwargs: P.kwargs) -> int:
        key = self.cache.key(self.func, *args, **kwargs)
        return self.cache.conn.delete(key)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        key = self.cache.key(self.func, *args, **kwargs)
        old_value = self.cache.conn.get(key)

        if old_value:
            log.debug("Hit cache for key %s", key)
            return self.cache.loader(old_value)

        value = self.func(*args, **kwargs)
        if isinstance(value, DontCache):
            return cast(T, value.unwrap())

        duration = self.cache.duration(self.func, *args, **kwargs)
        self.cache.conn.set(key, self.cache.dumper(value), ex=duration or None)
        return value
