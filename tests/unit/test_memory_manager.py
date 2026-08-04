def test_store_and_retrieve_turn(memory_manager):
    memory_manager.store_turn("session1", "user", "Hello!")
    turns = memory_manager.retrieve_memory("session1", 100)
    assert len(turns) == 1
    assert turns[0]["role"] == "user"


def test_sliding_window_eviction(memory_manager):
    memory_manager.sliding_window_size = 2
    memory_manager.store_turn("s1", "user", "1")
    memory_manager.store_turn("s1", "user", "2")
    memory_manager.store_turn("s1", "user", "3")
    stats = memory_manager.get_session_stats("s1")
    assert stats["turn_count"] == 2
    turns = memory_manager.retrieve_memory("s1", 100)
    assert turns[0]["content"] == "2"
    assert turns[1]["content"] == "3"


def test_token_bounded_retrieval(memory_manager):
    memory_manager.store_turn("s1", "user", "long " * 50)  # 50 tokens roughly
    memory_manager.store_turn("s1", "user", "long " * 50)
    turns = memory_manager.retrieve_memory("s1", 60)
    assert len(turns) == 1


def test_clear_session(memory_manager):
    memory_manager.store_turn("s1", "user", "1")
    memory_manager.clear_session("s1")
    assert len(memory_manager.retrieve_memory("s1", 100)) == 0


def test_session_stats(memory_manager):
    memory_manager.store_turn("s1", "user", "1")
    stats = memory_manager.get_session_stats("s1")
    assert stats["turn_count"] == 1
    assert stats["total_tokens"] > 0


def test_empty_session_retrieval(memory_manager):
    assert memory_manager.retrieve_memory("empty", 100) == []
