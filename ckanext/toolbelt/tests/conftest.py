import pytest

from ckan.lib import redis


@pytest.fixture()
def clean_cache():
    conn = redis.connect_to_redis()
    keys = conn.keys("*")
    if keys:
        conn.delete(*keys)
