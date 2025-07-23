from typing import List, Dict, Any
from pydantic import BaseModel
import tiktoken
import hashlib

class RetrievalDocument(BaseModel):
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any] = {}

class IntegratedRetrievalResult(BaseModel):
    selected_documents: List[RetrievalDocument]
    total_tokens_used: int
    documents_selected: int
    documents_dropped: int

class RetrievalIntegrator:
    """Integrates and ranks retrieval documents for context."""

    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def _get_content_hash(self, content: str) -> str:
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def process(self, documents: List[RetrievalDocument], max_tokens: int) -> IntegratedRetrievalResult:
        """Ranks, deduplicates, and selects documents within budget."""
        if not documents:
            return IntegratedRetrievalResult(
                selected_documents=[],
                total_tokens_used=0,
                documents_selected=0,
                documents_dropped=0
            )

        # Rank by relevance score descending
        sorted_docs = sorted(documents, key=lambda x: x.relevance_score, reverse=True)

        selected = []
        seen_hashes = set()
        current_tokens = 0
        documents_dropped = 0

        for doc in sorted_docs:
            content_hash = self._get_content_hash(doc.content)
            if content_hash in seen_hashes:
                documents_dropped += 1
                continue

            doc_tokens = len(self.tokenizer.encode(doc.content))
            if current_tokens + doc_tokens <= max_tokens:
                selected.append(doc)
                seen_hashes.add(content_hash)
                current_tokens += doc_tokens
            else:
                documents_dropped += 1

        return IntegratedRetrievalResult(
            selected_documents=selected,
            total_tokens_used=current_tokens,
            documents_selected=len(selected),
            documents_dropped=documents_dropped
        )
