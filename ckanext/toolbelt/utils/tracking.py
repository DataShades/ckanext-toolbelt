"""Event tracking utilities.

This module contains classes that can be used to count page visits, downloads,
api calls etc. The module itself does not contain hooks for tracking. It just
provides classes that can be used by existing hooks.

For example, popularity of certain endpoints can be tracked by counting visits
via middleware:

  >>> class MyPlugin(SingletonPlugin)
  >>>    implements(IMiddleware)
  >>>    def make_middleware(app):
  >>>        app.before_request(track_endpoint)
  >>>        return app
  >>>
  >>> def track_endpoint():
  >>>     track = Tracker("endpoint_visits")
  >>>     endpoint = ".".join(tk.get_endpoint())
  >>>     track.hit(endpoint)

So it's up to developer to initialize tracker and pass data to it. While
tracker itself is responsible for processing, storing, and obraining the
scores:

  >>> track = Tracker("endpoint_visits")
  >>> search_visits = track.score("dataset.search")

Data is stored in redis. It keeps trackers fast, but it also means that data
can be lost when redis is reloaded. If you are not using data persistence
features provided by redis, consider using tracker snapshots. Every tracker
class has `snapshot` method that exports data as a python structure. You can
save this structure somewhere:

  >>> snapshot = track.snapshot()
  >>> with open("/path/to/storage.json", "w") as dest:
  >>>     json.dump(snapshot, dest)

Later use it to restore data in redis via `restore` method. Keep in mind, that
`restore` **appends** data from the snapshot to existing data. If you want to
override existing data, call `reset` before using the snapshot.

  >>> ## optionally, remove current data
  >>> # track.reset()
  >>> with open("/path/to/storage.json") as src:
  >>>     snapshot = json.load(dest)
  >>> track.restore(snapshot)

"""
from __future__ import annotations

import dataclasses
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from hashlib import md5
from typing import TYPE_CHECKING, Any, Iterable, cast

from typing_extensions import NewType

import ckan.plugins.toolkit as tk
from ckan.lib.redis import connect_to_redis

if TYPE_CHECKING:
    from redis import Redis

log = logging.getLogger(__name__)
connect_to_redis: Any

Hash = NewType("Hash", str)


@dataclasses.dataclass()
class Tracker:
    """Simple events tracker.

    It counts and reports number of hits for a specific event and resembles
    `collections.Counter` in terms of functionality.

    >>> track = Tracker()
    >>> track.hit("hello")
    >>> track.hit("hello")
    >>> assert track.score("hello") == 2

    Default increase of score for every hit is 1. But it can be set to an
    arbitrary value via second argument of the `hit` method:

    >>> track = Tracker()
    >>> track.hit("hello", 3)
    >>> track.hit("hello", 7)
    >>> assert track.score("hello") == 10

    Trackers are created in global namespace. Pass a name to the tracker in
    order to count events separately:

    >>> global_track = Tracker()
    >>> my_track = Tracker("my_unique_name")
    >>> global_track.hit("hello", 10)
    >>> my_track.hit("hello", 5)
    >>>
    >>> assert Tracker().score("hello") == 10
    >>> assert Tracker("my_unique_name").score("hello") == 5

    Frequent events can be throttled(ignored for N seconds after successful hit):

    >>> track = Tracker(throttling_time=10)
    >>> track.hit("hello")
    >>> track.hit("hello")
    >>> assert track.score("hello") == 1
    >>>
    >>> sleep(15)
    >>> track.hit("hello")
    >>> track.hit("hello")
    >>> assert track.score("hello") == 2

    """

    name: dataclasses.InitVar[str] = "default"
    prefix: str = ""
    throttling_time: int = 0
    personalized: bool = False

    redis: Redis = dataclasses.field(default_factory=connect_to_redis)

    def __post_init__(self, name: str):
        if not self.prefix:
            site = tk.config["ckan.site_id"]
            self.prefix = f"{site}:tracker:{name}"

    def hash(self, event: str):
        """Return hashed value of event."""
        return Hash(md5(event.encode()).hexdigest())

    def throttle_key(self, hashed: Hash):
        """Compute key for throttling flag of the event hash."""
        if self.personalized:
            user = cast(str, tk.current_user.name)
            return f"{self.prefix}:throttle:{user}:{hashed}"

        return f"{self.prefix}:throttle:{hashed}"

    def is_throttling(self, hashed: Hash):
        """Check if event hash is throttling."""
        return bool(self.redis.exists(self.throttle_key(hashed)))

    def throttle(self, hashed: Hash):
        """Start throttling the hash of event."""
        if self.throttling_time:
            self.redis.set(self.throttle_key(hashed), 1, ex=self.throttling_time)

    def unthrottle(self, hashed: Hash):
        """Stop throttling the hash of event."""
        self.redis.delete(self.throttle_key(hashed))

    def ignore_key(self):
        """Compute key of ignorelist."""
        return f"{self.prefix}:ignore"

    def is_ignored(self, hashed: Hash):
        """Check if event is ignored(hits are not tracked)."""
        return self.redis.sismember(self.ignore_key(), hashed)

    def ignore(self, hashed: Hash):
        """Add event's hash to ignorelist."""
        return self.redis.sadd(self.ignore_key(), hashed)

    def unignore(self, hashed: Hash):
        """Remove event's hash from ignorelist."""
        return self.redis.srem(self.ignore_key(), hashed)

    def trans_key(self):
        """Compute key for translation table."""
        return f"{self.prefix}:trans"

    def add_trans(self, event: str) -> Hash:
        """Add event to the translation table."""
        hashed = self.hash(event)
        self.redis.hset(self.trans_key(), hashed, event)
        return hashed

    def remove_trans(self, hashed: Hash):
        """Remove event from the translation table by hash."""
        self.redis.hdel(self.trans_key(), hashed)

    def translate(self, hashed: Hash) -> str | None:
        """Restore event name from its hash."""
        event: bytes | None = self.redis.hget(self.trans_key(), hashed)
        if event is None:
            return None

        return event.decode()

    def distribution_key(self):
        """Compute key for scores table."""
        return f"{self.prefix}:distribution"

    def member_key(self, hashed: Hash) -> str:
        """Compute name for event's hash inside the score table."""
        return hashed

    def hit(self, event: str, count: float = 1, **kwargs: Any):
        """Increase event's score."""
        hashed = self.hash(event)

        if self.is_ignored(hashed):
            return

        if self.is_throttling(hashed):
            return

        self.throttle(hashed)

        self.add_trans(event)
        self.update_score(hashed, count, **kwargs)

    def update_score(self, hashed: Hash, count: float, **kwargs: Any):
        """Update score directly, bypassing all checks, like ignorelist or
        throttling.

        """
        self.redis.zincrby(self.distribution_key(), count, self.member_key(hashed))

    def get_score(self, hashed: Hash, **kwargs: Any) -> float | None:
        """Get score from redis, without performing any type-casting or value coercion."""
        return self.redis.zscore(self.distribution_key(), self.member_key(hashed))

    def score(self, event: str, **kwargs: Any) -> float:
        """Return event's score."""
        hashed = self.hash(event)

        score = self.get_score(hashed, **kwargs)
        if score is None:
            return 0

        return score

    def drop(self, event: str):
        """Remove event scores."""
        hashed = self.hash(event)
        dk = self.distribution_key()

        self.redis.zrem(dk, self.member_key(hashed))
        self.remove_trans(hashed)

    def reset(self):
        """Remove data related to the current tracker."""
        if keys := self.redis.keys(f"{self.prefix}:*"):
            self.redis.delete(*keys)

    def snapshot(self):
        """Export tracker data."""
        data: dict[bytes, dict[str, Any]] = {
            hash: {"event": event.decode(), "score": 0}
            for hash, event in self.redis.hgetall(self.trans_key()).items()
        }
        for k, v in self.redis.zscan_iter(self.distribution_key()):
            data[k]["score"] = float(v)

        return list(data.values())

    def restore(self, snapshot: list[dict[str, Any]]):
        """Restore data from the snapshot."""
        for record in snapshot:
            self.add_trans(record["event"])
            self.update_score(self.hash(record["event"]), record["score"])

    def most_common(self, num: int) -> Iterable[dict[str, str | float]]:
        """Return `num` most popular events with scores."""
        scores: list[tuple[bytes, float]] = self.redis.zrange(
            self.distribution_key(),
            0,
            num - 1,
            desc=True,
            withscores=True,
        )

        for k, v in scores:
            event = self.translate(Hash(k.decode()))
            if not event:
                continue
            yield {"event": event, "score": v}


@dataclasses.dataclass()
class DateTracker(Tracker):
    """Track events within a timeframe.

    This tracker groups event by the time when event was recorded.

    Granularity of tracking is defined by the `date_format` attribute of the
    tracker. By default it groups hits by date, but it's possible to group them
    by hour or even minute:

    >>> hour = DateTracker(date_format="%Y-%m-%d %H")
    >>> minute = DateTracker(date_format="%Y-%m-%d %H:%M")

    """

    # aggregation prefix for events. By default, events are grouped by date. If
    # you want to put events from the whole month into a single score, use
    # "%Y-%m" format. If you want to track separately every hour, use "%Y-%m-%d
    # %H", etc.
    date_format: str = "%Y-%m-%d"

    # number of seconds before hit marked as expired and removed. It relies on
    # `date_format`, so it has no sense to make `max_age` smaller than
    # granularity of `date_format`. I.e, if you are using default `date_format`
    # that combine hits by date, max age should be more than one day.
    max_age: int = 60 * 60 * 24 * 365

    # number of seconds before value of hits will be reduced
    obsoletion_period: int = 60 * 60 * 24 * 365 * 10

    def member_key(self, hashed: Hash, moment: datetime | None = None) -> str:
        """Compute name for event's hash inside the score table."""
        date_stem = self.format_date_stem(moment or self.now())
        return f"{date_stem}/{hashed}"

    def format_date_stem(self, date: datetime):
        """Transrom date into a prefix for score key."""
        return date.strftime(self.date_format)

    def drop(self, event: str):
        """Remove event scores."""
        hashed = self.hash(event)
        dk = self.distribution_key()

        series: Iterable[tuple[bytes, float]] = self.redis.zscan_iter(dk, f"*/{hashed}")

        if keys := [s[0] for s in series]:
            self.redis.zrem(dk, *keys)

        self.remove_trans(hashed)
        self.redis.zrem(self.most_common_key(), hashed)

    def moment_score(self, event: str, moment: datetime | None = None) -> float:
        """Return event's score for specific period."""
        hashed = self.hash(event)

        score: float | None = self.redis.zscore(
            self.distribution_key(),
            self.member_key(hashed, moment),
        )
        if score is None:
            return 0

        return float(score)

    def update_score(
        self,
        hashed: Hash,
        count: float,
        moment: datetime | None = None,
        **kwargs: Any,
    ):
        """Update score directly, bypassing all checks, like ignorelist or
        throttling.

        """
        mk = self.member_key(hashed, moment)
        self.redis.zincrby(self.distribution_key(), count, mk)

    def get_score(
        self,
        hashed: Hash,
        moment: datetime | None = None,
        **kwargs: Any,
    ) -> float | None:
        """Get score from redis, accumulating event scores from all dates."""
        dk = self.distribution_key()
        series: Iterable[tuple[bytes, float]] = self.redis.zscan_iter(dk, f"*/{hashed}")
        value = 0

        for k, v in series:
            date_str = k.split(b"/", 1)[0]
            try:
                date = datetime.strptime(date_str.decode(), self.date_format)
            except ValueError:
                continue
            age = self.now() - date
            value += self._scale_score(v, age.total_seconds())
        return value

    def snapshot(self):
        """Export tracker data."""
        data: dict[bytes, dict[str, Any]] = {
            hash: {"event": event.decode(), "records": []}
            for hash, event in self.redis.hgetall(self.trans_key()).items()
        }
        dist: Iterable[tuple[bytes, float]] = self.redis.zscan_iter(
            self.distribution_key(),
        )
        for k, v in dist:
            date_str, hashed = k.split(b"/", 1)
            try:
                date = datetime.strptime(date_str.decode(), self.date_format)
            except ValueError:
                continue

            data[hashed]["records"].append(
                {"date": date.isoformat(), "score": float(v)},
            )

        return list(data.values())

    def restore(self, snapshot: list[dict[str, Any]]):
        """Restore data from the snapshot."""
        for item in snapshot:
            self.add_trans(item["event"])
            hashed = self.hash(item["event"])

            for record in item["records"]:
                moment = datetime.fromisoformat(record["date"])
                self.update_score(hashed, record["score"], moment=moment)

    def _scale_score(self, score: float, age: float):
        """Compute reduced value of score according to its age."""
        return float(score) / (age // self.obsoletion_period + 1)

    def refresh(self):
        """Rebuild most_common table."""
        max_age = timedelta(seconds=self.max_age)
        dk = self.distribution_key()
        sk = self.most_common_key()

        expired_dist: set[bytes] = set()
        distribution: Iterable[tuple[bytes, float]] = self.redis.zscan_iter(dk)

        scores: dict[bytes, float] = defaultdict(float)

        for k, v in distribution:
            date_str, hashed = k.split(b"/", 1)
            try:
                date = datetime.strptime(date_str.decode(), self.date_format)
            except ValueError:
                log.exception("Remove invalid key %s", k)
                expired_dist.add(k)
                continue

            age = self.now() - date

            if age > max_age:
                expired_dist.add(k)
                continue

            scores[hashed] += self._scale_score(v, age.total_seconds())

        if expired_dist:
            self.redis.zrem(dk, *expired_dist)

        expired_scores: set[bytes] = set()
        common_distribution: Iterable[tuple[bytes, float]] = self.redis.zscan_iter(sk)
        for k, v in common_distribution:
            if k not in scores:
                expired_scores.add(k)
                continue

        if scores:
            self.redis.zadd(sk, cast(Any, scores))

        if expired_scores:
            self.redis.zrem(sk, *expired_scores)
            self.redis.hdel(self.trans_key(), *expired_scores)

    def now(self):
        """Return current time."""
        return datetime.now()

    def most_common_key(self):
        """Compute key for the most_common table."""
        return f"{self.prefix}:most_common"

    def most_common(self, num: int) -> Iterable[dict[str, str | float]]:
        """Return `num` most popular events with scores."""
        scores: list[tuple[bytes, float]] = self.redis.zrange(
            self.most_common_key(),
            0,
            num - 1,
            desc=True,
            withscores=True,
        )

        for k, v in scores:
            event = self.translate(Hash(k.decode()))
            if not event:
                continue
            yield {"event": event, "score": v}
