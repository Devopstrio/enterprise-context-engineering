from context_engineering.assembler.context_assembler import ContextAssemblyRequest
from context_engineering.retrieval.retrieval_integrator import RetrievalDocument


def test_full_context_assembly(assembler, memory_manager):
    memory_manager.store_turn("sess1", "user", "prev")
    req = ContextAssemblyRequest(
        system_prompt="sys",
        user_input="user",
        session_id="sess1",
        model_name="test-model",
        max_tokens=1000,
        retrieval_documents=[RetrievalDocument(content="doc1", source="s1", relevance_score=0.9)],
    )
    res = assembler.assemble(req)
    assert len(res.final_context) == 3  # sys + prev + user
    assert "doc1" in res.final_context[0]["content"]  # doc inserted in system prompt


def test_assembly_with_compression(assembler):
    req = ContextAssemblyRequest(
        system_prompt="sys",
        user_input="user",
        session_id="sess2",
        model_name="test",
        max_tokens=20,  # Very small to force compression
        retrieval_documents=[RetrievalDocument(content="very long text here " * 50, source="s1", relevance_score=0.9)],
    )
    res = assembler.assemble(req)
    assert res.total_tokens < 1000  # Should be compressed


def test_assembly_without_retrieval(assembler):
    req = ContextAssemblyRequest(
        system_prompt="sys",
        user_input="user",
        session_id="sess3",
        model_name="test",
        max_tokens=1000,
    )
    res = assembler.assemble(req)
    assert res.final_context[0]["content"] == "sys"


def test_assembly_audit_logging(assembler, audit_logger):
    req = ContextAssemblyRequest(
        system_prompt="sys",
        user_input="user",
        session_id="sess4",
        model_name="test",
        max_tokens=1000,
    )
    assembler.assemble(req)
    events = audit_logger.get_recent_events()
    assert len(events) > 0
    assert any(e["event_type"] == "ASSEMBLY_STARTED" for e in events)
