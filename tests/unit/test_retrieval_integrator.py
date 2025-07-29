import pytest
from context_engineering.retrieval.retrieval_integrator import RetrievalDocument

def test_rank_documents_by_relevance(retrieval_integrator):
    docs = [
        RetrievalDocument(content="Low", source="1", relevance_score=0.1),
        RetrievalDocument(content="High", source="2", relevance_score=0.9),
    ]
    res = retrieval_integrator.process(docs, 1000)
    assert res.selected_documents[0].source == "2"

def test_select_within_budget(retrieval_integrator):
    docs = [
        RetrievalDocument(content="very long " * 50, source="1", relevance_score=0.9),
        RetrievalDocument(content="short", source="2", relevance_score=0.8),
    ]
    res = retrieval_integrator.process(docs, 20)
    assert len(res.selected_documents) == 1
    assert res.selected_documents[0].source == "2" # Long one didn't fit, short one did

def test_deduplicate_documents(retrieval_integrator):
    docs = [
        RetrievalDocument(content="Same content", source="1", relevance_score=0.9),
        RetrievalDocument(content="Same content", source="2", relevance_score=0.8),
    ]
    res = retrieval_integrator.process(docs, 1000)
    assert len(res.selected_documents) == 1
    assert res.documents_dropped == 1

def test_empty_documents(retrieval_integrator):
    res = retrieval_integrator.process([], 1000)
    assert len(res.selected_documents) == 0
