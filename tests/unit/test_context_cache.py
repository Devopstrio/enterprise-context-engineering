def test_cache_store_and_retrieve(cache):
    cache.cache_context("key1", {"context": "test"}, 10)
    assert cache.get_cached_context("key1") == {"context": "test"}


def test_cache_ttl_expiration(cache):
    cache.cache_context("key1", {"context": "test"}, -1)  # Expired
    assert cache.get_cached_context("key1") is None


def test_cache_invalidation(cache):
    cache.cache_context("key1", {"context": "test"}, 10)
    cache.invalidate("key1")
    assert cache.get_cached_context("key1") is None


def test_cache_stats(cache):
    cache.cache_context("key1", {"context": "test"}, 10)
    cache.get_cached_context("key1")
    cache.get_cached_context("miss")
    stats = cache.get_cache_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
