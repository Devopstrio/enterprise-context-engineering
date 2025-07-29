import pytest

def test_compress_long_text(compressor):
    text = "This is a very long text. " * 50
    res = compressor.compress(text, 20)
    assert res.compressed_tokens <= 20
    assert res.sentences_dropped > 0

def test_compress_short_text_no_change(compressor):
    text = "Short text."
    res = compressor.compress(text, 100)
    assert res.compressed_tokens == res.original_tokens
    assert res.sentences_dropped == 0

def test_compression_ratio(compressor):
    text = "Sentence one. Sentence two."
    res = compressor.compress(text, 3)
    assert res.compression_ratio < 1.0

def test_compress_empty_text(compressor):
    res = compressor.compress("", 10)
    assert res.compressed_tokens == 0
