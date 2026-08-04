import re

import tiktoken
from pydantic import BaseModel


class CompressionResult(BaseModel):
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    sentences_kept: int
    sentences_dropped: int


class ContextCompressor:
    """Compresses context to fit target token count."""

    def __init__(self) -> None:
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def compress(self, text: str, target_tokens: int) -> CompressionResult:
        if not text:
            return CompressionResult(
                compressed_text="",
                original_tokens=0,
                compressed_tokens=0,
                compression_ratio=0.0,
                sentences_kept=0,
                sentences_dropped=0,
            )

        original_tokens = len(self.tokenizer.encode(text))
        if original_tokens <= target_tokens:
            return CompressionResult(
                compressed_text=text,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                sentences_kept=len(self._split_sentences(text)),
                sentences_dropped=0,
            )

        sentences = self._split_sentences(text)
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            # Basic scoring: position (earlier is better), length
            score = (len(sentences) - i) + (len(sentence) * 0.1)
            scored_sentences.append((score, i, sentence))

        # Sort by score descending
        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        selected_indices = []
        current_tokens = 0

        for _score, idx, sentence in scored_sentences:
            sentence_tokens = len(self.tokenizer.encode(sentence + " "))
            if current_tokens + sentence_tokens <= target_tokens:
                selected_indices.append(idx)
                current_tokens += sentence_tokens

        selected_indices.sort()
        compressed_sentences = [sentences[idx] for idx in selected_indices]
        compressed_text = " ".join(compressed_sentences)

        compressed_tokens = len(self.tokenizer.encode(compressed_text))
        sentences_kept = len(selected_indices)
        sentences_dropped = len(sentences) - sentences_kept

        return CompressionResult(
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0.0,
            sentences_kept=sentences_kept,
            sentences_dropped=sentences_dropped,
        )

    def _split_sentences(self, text: str) -> list[str]:
        # Simple regex for sentence splitting
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]
