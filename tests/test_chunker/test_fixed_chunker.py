"""Tests for fixed chunker."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 테스트 파일은 FixedChunker가 올바르게 텍스트를 나누는지 확인하는 간단한 검사예요.
# 주요 포인트:
# - 작은 텍스트는 하나의 청크로, 긴 텍스트는 여러 청크로 나뉘는지 확인합니다.
# - 메타데이터(출처, 인덱스 등)가 제대로 설정되는지 검사합니다.

import pytest
from src.chunker.fixed_chunker import FixedChunker


class TestFixedChunker:
    """Test cases for FixedChunker."""

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        chunker = FixedChunker(chunk_size=1000, chunk_overlap=200)
        text = "This is a short text."
        chunks = chunker.chunk(text, source="test")

        assert len(chunks) == 1
        assert chunks[0].content == text

    def test_chunk_long_text(self):
        """Test chunking text longer than chunk size."""
        chunker = FixedChunker(chunk_size=100, chunk_overlap=20)
        text = "This is a sentence. " * 20
        chunks = chunker.chunk(text, source="test")

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.content) <= 100 + 50  # Allow some flexibility

    def test_chunk_metadata(self):
        """Test chunk metadata."""
        chunker = FixedChunker(chunk_size=100, chunk_overlap=20)
        text = "Test content for chunking."
        chunks = chunker.chunk(text, source="test_source")

        assert chunks[0].source == "test_source"
        assert "chunk_index" in chunks[0].metadata
