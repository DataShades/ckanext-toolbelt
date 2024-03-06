from __future__ import annotations
from datetime import datetime
from operator import itemgetter
import pytest
from faker import Faker
from ckanext.toolbelt.utils.tracking import Tracker, DateTracker


@pytest.fixture()
def tracker_factory():
    return Tracker


@pytest.fixture()
def tracker(faker: Faker, tracker_factory: type[Tracker]):
    return tracker_factory(faker.word())


@pytest.mark.usefixtures("clean_redis")
class TestAllTrackers:
    @pytest.fixture(params=[Tracker, DateTracker])
    def tracker_factory(self, request: pytest.FixtureRequest):
        return request.param

    def test_hits(self, tracker: Tracker, faker: Faker):
        """Each event tracked separately."""
        event = faker.word()
        another_event = faker.word()
        n = 10

        for idx in range(n):
            tracker.hit(event)
            if idx % 2:
                tracker.hit(another_event)

        assert tracker.score(event) == n
        assert tracker.score(another_event) == n // 2

    def test_namespaces(self, tracker_factory: type[Tracker], faker: Faker):
        """Trackers created with the same name share the data."""
        event = faker.word()
        name = faker.word()

        global_count, named_count = faker.pyint(), faker.pyint()

        global_track = tracker_factory()
        named_track = tracker_factory(name)

        global_track.hit(event, global_count)
        named_track.hit(event, named_count)

        assert tracker_factory().score(event) == global_count
        assert tracker_factory(name).score(event) == named_count

    def test_throttling(self, tracker_factory: type[Tracker], faker: Faker):
        """Throttling ignores duplicated events for certain amount of time."""
        event = faker.word()
        track = tracker_factory(throttling_time=10)
        track.hit(event)
        track.hit(event)
        assert track.score(event) == 1

        track.unthrottle(track.hash(event))

        track.hit(event)
        track.hit(event)
        assert track.score(event) == 2

    def test_ignoring(self, tracker_factory: type[Tracker], faker: Faker):
        """Ignored events are not tracked at all."""
        event = faker.word()
        track = tracker_factory()
        hash = track.hash(event)
        track.ignore(hash)

        track.hit(event)
        track.hit(event)
        assert track.score(event) == 0

        track.unignore(hash)

        track.hit(event)
        track.hit(event)
        assert track.score(event) == 2

    def test_translations(self, tracker: Tracker, faker: Faker):
        """Tracker can restore event name from it's hash"""
        event = faker.word()
        tracker.hit(event)
        hash = tracker.hash(event)

        assert tracker.translate(hash) == event

    def test_drop(self, tracker: Tracker, faker: Faker):
        """Event scores can be removed"""
        event = faker.word()
        tracker.hit(event)
        tracker.drop(event)
        assert tracker.score(event) == 0

    def test_reset(self, tracker: Tracker, faker: Faker):
        """Tracker data can be removed"""
        for _ in range(10):
            tracker.hit(faker.word())
        tracker.reset()

        assert not tracker.snapshot()

    def test_most_common(self, tracker: Tracker, faker: Faker):
        """Most common items ordered by score"""
        first_event = faker.word()
        second_event = faker.word()
        third_event = faker.word()

        tracker.hit(first_event, 100)
        tracker.hit(second_event, 50)
        tracker.hit(third_event, 200)

        if isinstance(tracker, DateTracker):
            tracker.refresh()

        assert list(tracker.most_common(1)) == [{"event": third_event, "score": 200}]
        assert list(tracker.most_common(2)) == [
            {"event": third_event, "score": 200},
            {"event": first_event, "score": 100},
        ]
        assert list(tracker.most_common(3)) == [
            {"event": third_event, "score": 200},
            {"event": first_event, "score": 100},
            {"event": second_event, "score": 50},
        ]


@pytest.mark.usefixtures("clean_redis")
class TestTracker:
    def test_snapshot(self, tracker: Tracker, faker: Faker):
        """Tracker data has expected snapshot format."""
        first_event = faker.word()
        second_event = faker.word()
        first_count = faker.pyint()
        second_count = faker.pyint()
        tracker.hit(first_event, first_count)
        tracker.hit(second_event, second_count)
        assert sorted(tracker.snapshot(), key=itemgetter("event")) == sorted(
            [
                {"event": first_event, "score": first_count},
                {"event": second_event, "score": second_count},
            ],
            key=itemgetter("event"),
        )

    def test_restore(self, tracker: Tracker, faker: Faker):
        """Tracker data can be restored from snapshot format."""
        first_event = faker.word()
        second_event = faker.word()
        first_count = faker.pyint()
        second_count = faker.pyint()
        tracker.restore(
            [
                {"event": first_event, "score": first_count},
                {"event": second_event, "score": second_count},
            ],
        )
        assert tracker.score(first_event) == first_count
        assert tracker.score(second_event) == second_count


@pytest.mark.usefixtures("clean_redis")
class TestDateTracker:
    @pytest.fixture()
    def tracker_factory(self):
        return DateTracker

    def test_moment_interactions(self, tracker, faker):
        """Past scores can be updated and shown.
        """
        date = faker.date_time_between(end_date="-2d")
        event = faker.word()
        tracker.hit(event, moment=date)

        assert tracker.score(event) == 0
        assert tracker.score(event, moment=date) == 1


    def test_snapshot(self, tracker: DateTracker, faker: Faker):
        """Tracker data has expected snapshot format."""
        first_event = faker.word()
        second_event = faker.word()
        first_count = faker.pyint()
        second_count = faker.pyint()
        tracker.hit(first_event, first_count)
        tracker.hit(second_event, second_count)

        date = datetime.strptime(
            tracker.format_date_stem(tracker.now()), tracker.date_format,
        )

        assert sorted(tracker.snapshot(), key=itemgetter("event")) == sorted(
            [
                {
                    "event": first_event,
                    "records": [{"date": date.isoformat(), "score": first_count}],
                },
                {
                    "event": second_event,
                    "records": [{"date": date.isoformat(), "score": second_count}],
                },
            ],
            key=itemgetter("event"),
        )

    def test_restore(self, tracker: DateTracker, faker: Faker):
        """Tracker data can be restored from snapshot format."""
        first_event = faker.word()
        second_event = faker.word()
        first_count = faker.pyint()
        second_count = faker.pyint()
        date = datetime.strptime(
            tracker.format_date_stem(tracker.now()), tracker.date_format,
        )

        tracker.restore(
            [
                {
                    "event": first_event,
                    "records": [{"date": date.isoformat(), "score": first_count}],
                },
                {
                    "event": second_event,
                    "records": [{"date": date.isoformat(), "score": second_count}],
                },
            ],
        )
        assert tracker.score(first_event) == first_count
        assert tracker.score(second_event) == second_count
