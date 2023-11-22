from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
import dataclasses
import logging
from hashlib import md5
from typing import Any, Iterable, cast
from typing_extensions import NewType
from ckan.lib.redis import connect_to_redis
import ckan.plugins.toolkit as tk
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

    redis: Redis[bytes] = dataclasses.field(default_factory=connect_to_redis)

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
            user = tk.current_user.name
            return f"{self.prefix}:throttle:{user}:{hashed}"

        return f"{self.prefix}:throttle:{hashed}"

    def is_throttling(self, hashed: Hash):
        """Check if event hash is throttling."""
        return self.redis.exists(self.throttle_key(hashed))

    def throttle(self, hashed: Hash):
        """Start throttling the hash of event"""
        if self.throttling_time:
            self.redis.set(self.throttle_key(hashed), 1, ex=self.throttling_time)

    def unthrottle(self, hashed: Hash):
        """Stop throttling the hash of event"""
        self.redis.delete(self.throttle_key(hashed))

    def ignore_key(self):
        """Compute key of ignorelist"""
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
        """Restore event name from its hash"""
        event = self.redis.hget(self.trans_key(), hashed)
        if event is None:
            return

        return event.decode()

    def distribution_key(self):
        """Compute key for scores table."""
        return f"{self.prefix}:distribution"

    def member_key(self, hashed: Hash) -> str:
        """Compute name for event's hash inside the score table."""
        return hashed

    def hit(self, event: str, count: int = 1):
        """Increase event's score."""
        hashed = self.hash(event)

        if self.is_ignored(hashed):
            return

        if self.is_throttling(hashed):
            return

        self.throttle(hashed)

        self.add_trans(event)

        self.redis.zincrby(self.distribution_key(), count, self.member_key(hashed))

    def score(self, event: str) -> float:
        """Return event's score"""
        hashed = self.hash(event)

        score = self.redis.zscore(self.distribution_key(), self.member_key(hashed))
        if score is None:
            return 0

        return float(score)

    def drop(self, event: str):
        """Remove event scores"""
        hashed = self.hash(event)
        dk = self.distribution_key()

        self.redis.zrem(dk, self.member_key(hashed))
        self.remove_trans(hashed)

    def reset(self):
        """Remove data related to the current tracker."""
        if keys := self.redis.keys(f"{self.prefix}:*"):
            self.redis.delete(*keys)

    def export(self):
        """Export tracker data."""
        data: dict[bytes, dict[str, Any]] = {
            hash: {"event": event.decode(), "score": 0}
            for hash, event in self.redis.hgetall(self.trans_key()).items()
        }
        for k, v in self.redis.zscan_iter(self.distribution_key()):
            data[k]["score"] = int(v)

        return list(data.values())

    def most_common(self, num: int) -> Iterable[dict[str, str | float]]:
        """Return `num` most popular events with scores."""
        scores: list[tuple[bytes, float]] = self.redis.zrange(
            self.distribution_key(), 0, num - 1, desc=True, withscores=True
        )

        for k, v in scores:
            event = self.translate(Hash(k.decode()))
            if not event:
                continue
            yield {"event": event, "score": v}


@dataclasses.dataclass()
class DateTracker(Tracker):
    """Track events within a timeframe.

    This tracker groups event by the time when event was recorded and return
    scores only from the latest period.

    Granularity of tracking is defined by the `date_format` attribute of the
    tracker. By default it groups hits by date, but it's possible to group them
    by hour or even minute:

    >>> hour = DateTracker(date_format="%Y-%m-%d %H")
    >>> minute = DateTracker(date_format="%Y-%m-%d %H:%M")

    """

    date_format: str = "%Y-%m-%d"
    max_age: int = 60 * 60 * 24 * 365
    obsoletion_period: int = 60 * 60 * 24 * 365 * 10

    def member_key(self, hashed: Hash, moment: datetime | None = None) -> str:
        """Compute name for event's hash inside the score table."""
        date_stem = self.format_date_stem(moment or self.now())
        return f"{date_stem}/{hashed}"

    def format_date_stem(self, date: datetime):
        """Transrom date into a prefix for score key."""
        return date.strftime(self.date_format)

    def drop(self, event: str):
        """Remove event scores"""
        hashed = self.hash(event)
        dk = self.distribution_key()

        series = self.redis.zscan_iter(dk, f"*/{hashed}")

        if keys := [s[0] for s in series]:
            self.redis.zrem(dk, *keys)

        self.remove_trans(hashed)
        self.redis.zrem(self.most_common_key(), hashed)

    def moment_score(self, event: str, moment: datetime) -> float:
        """Return event's score for specific period"""
        hashed = self.hash(event)

        score = self.redis.zscore(
            self.distribution_key(), self.member_key(hashed, moment)
        )
        if score is None:
            return 0

        return float(score)

    def export(self):
        """Export tracker data."""
        data: dict[bytes, dict[str, Any]] = {
            hash: {"event": event.decode(), "records": []}
            for hash, event in self.redis.hgetall(self.trans_key()).items()
        }
        for k, v in self.redis.zscan_iter(self.distribution_key()):
            date_str, hashed = k.split(b"/", 1)
            try:
                date = datetime.strptime(date_str.decode(), self.date_format)
            except ValueError:
                continue

            data[hashed]["records"].append({"date": date.isoformat(), "count": int(v)})

        return list(data.values())

    def refresh(self):
        """Rebuild most_common table."""
        max_age = timedelta(seconds=self.max_age)
        dk = self.distribution_key()
        sk = self.most_common_key()

        expired_dist: set[bytes] = set()
        distribution = self.redis.zscan_iter(dk)

        scores: dict[bytes, float] = defaultdict(float)

        for k, v in distribution:
            date_str, hashed = k.split(b"/", 1)
            try:
                date = datetime.strptime(date_str.decode(), self.date_format)
            except ValueError:
                log.error("Remove invalid key %s", k)
                expired_dist.add(k)
                continue

            age = self.now() - date

            if age > max_age:
                expired_dist.add(k)
                continue

            scores[hashed] += int(v) / (age.seconds // self.obsoletion_period + 1)

        if expired_dist:
            self.redis.hdel(dk, *expired_dist)

        expired_scores: set[bytes] = set()
        for k, v in self.redis.zscan_iter(sk):
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
        return datetime.utcnow()

    def most_common_key(self):
        """Compute key for the most_common table."""
        return f"{self.prefix}:most_common"

    def most_common(self, num: int) -> Iterable[dict[str, str | float]]:
        """Return `num` most popular events with scores."""
        scores: list[tuple[bytes, float]] = self.redis.zrange(
            self.most_common_key(), 0, num - 1, desc=True, withscores=True
        )

        for k, v in scores:
            event = self.translate(Hash(k.decode()))
            if not event:
                continue
            yield {"event": event, "score": v}
