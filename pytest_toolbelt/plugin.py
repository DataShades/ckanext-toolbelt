from __future__ import annotations

import pytest

import ckan.plugins.core as pcore
from ckan.tests.pytest_ckan import fixtures

if not hasattr(pcore, "unload_non_system_plugins"):

    @pytest.fixture()
    def with_plugins(ckan_config):
        """Override CKAN `with_plugins` unloading **all** plugins, even if they
        are not listed in `ckan.plugins`.

        """
        pcore.load_all()
        yield

        system_plugins = pcore.find_system_plugins()
        plugins_to_unload = [
            p
            for p in reversed(pcore._PLUGINS)  # type: ignore
            if p not in system_plugins
        ]
        pcore.unload(*plugins_to_unload)


if fixtures.migrate_db_for._pytestfixturefunction.scope == "function":

    @pytest.fixture(scope="session")
    def migrate_db_for():
        """Override CKAN `migrate_db_for` using `session` scope for fixture."""

        from ckan.cli.db import _run_migrations

        def runner(plugin, version="head", forward=True):
            assert plugin, "Cannot apply migrations of unknown plugin"
            _run_migrations(plugin, version, forward)

        return runner


if not hasattr(fixtures, "reset_db_once") and not hasattr(fixtures, "non_clean_db"):

    @pytest.fixture(scope="session")
    def reset_db_once(reset_db):
        """Internal fixture that cleans DB only the first time it's used."""
        reset_db()

    @pytest.fixture(scope="function")
    def non_clean_db(reset_db_once):
        """Guarantees that DB is initialized.

        This fixture either initializes DB if it hasn't been done yet or does
        nothing otherwise. If there is some data in DB, it stays intact. If your
        tests need empty database, use `clean_db` instead, which is much slower,
        but guarantees that there are no data left from the previous test session.

        Example::

            @pytest.mark.usefixtures("non_clean_db")
            def test_example():
                assert factories.User()

        """
        from ckan import model

        model.repo.init_db()


if not hasattr(fixtures, "reset_redis") and not hasattr(fixtures, "clean_redis"):

    @pytest.fixture(scope="session")
    def reset_redis():
        """Callable for removing all keys from Redis.
        Accepts redis key-pattern for narrowing down the list of items to
        remove. By default removes everything.
        This fixture removes all the records from Redis on call::
            def test_redis_is_empty(reset_redis):
                redis = connect_to_redis()
                redis.set("test", "test")
                reset_redis()
                assert not redis.get("test")
        If only specific records require removal, pass a pattern to the fixture::
            def test_redis_is_empty(reset_redis):
                redis = connect_to_redis()
                redis.set("AAA-1", 1)
                redis.set("AAA-2", 2)
                redis.set("BBB-3", 3)
                reset_redis("AAA-*")
                assert not redis.get("AAA-1")
                assert not redis.get("AAA-2")
                assert redis.get("BBB-3") is not None
        """

        def cleaner(pattern: str = "*") -> int:
            """Remove keys matching pattern.
            Return number of removed records.
            """
            from ckan.lib.redis import connect_to_redis

            conn = connect_to_redis()
            keys = conn.keys(pattern)
            if keys:
                return conn.delete(*keys)
            return 0

        return cleaner

    @pytest.fixture()
    def clean_redis(reset_redis):
        """Remove all keys from Redis.
        This fixture removes all the records from Redis::
            @pytest.mark.usefixtures("clean_redis")
            def test_redis_is_empty():
                assert redis.keys("*") == []
        If test requires presence of some initial data in redis, make sure that
        data producer applied **after** ``clean_redis``::
            @pytest.mark.usefixtures(
                "clean_redis",
                "fixture_that_adds_xxx_key_to_redis"
            )
            def test_redis_has_one_record():
                assert redis.keys("*") == [b"xxx"]
        """
        reset_redis()


if not hasattr(fixtures, "app_with_session"):

    @pytest.fixture()
    def app_with_session(make_app):
        from flask.sessions import SecureCookieSessionInterface

        app = make_app()
        app.flask_app.session_interface = SecureCookieSessionInterface()
        return app
