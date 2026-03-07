"""Tests for base retriever."""

import pytest
from src.retriever.base_retriever import BaseRetriever, RetrievalResult


class ConcreteRetriever(BaseRetriever):
    """Concrete implementation for testing."""

    def __init__(self, results: list[RetrievalResult] | None = None, top_k: int = 5):
        super().__init__(top_k=top_k)
        self.results = results or []

    def retrieve(self, query: str) -> list[RetrievalResult]:
        return self.results[: self.top_k]


class TestRetrievalResult:
    """Test cases for RetrievalResult dataclass."""

    def test_creation(self):
        """Test RetrievalResult creation."""
        result = RetrievalResult(
            content="Test content",
            metadata={"key": "value"},
            score=0.95,
            source="test_source.txt",
        )

        assert result.content == "Test content"
        assert result.metadata == {"key": "value"}
        assert result.score == 0.95
        assert result.source == "test_source.txt"

    def test_creation_with_empty_metadata(self):
        """Test RetrievalResult with empty metadata."""
        result = RetrievalResult(
            content="Content",
            metadata={},
            score=0.5,
            source="source",
        )

        assert result.metadata == {}

    def test_creation_with_complex_metadata(self):
        """Test RetrievalResult with complex metadata."""
        metadata = {
            "title": "Document Title",
            "author": "Author Name",
            "tags": ["tag1", "tag2"],
            "nested": {"key": "value"},
        }
        result = RetrievalResult(
            content="Content",
            metadata=metadata,
            score=0.8,
            source="source",
        )

        assert result.metadata["title"] == "Document Title"
        assert result.metadata["tags"] == ["tag1", "tag2"]
        assert result.metadata["nested"]["key"] == "value"

    def test_score_range(self):
        """Test that score can be any float value."""
        # High score
        result1 = RetrievalResult(content="", metadata={}, score=1.0, source="")
        assert result1.score == 1.0

        # Zero score
        result2 = RetrievalResult(content="", metadata={}, score=0.0, source="")
        assert result2.score == 0.0

        # Negative score (some algorithms may produce this)
        result3 = RetrievalResult(content="", metadata={}, score=-0.5, source="")
        assert result3.score == -0.5


class TestBaseRetriever:
    """Test cases for BaseRetriever."""

    def test_initialization_default_top_k(self):
        """Test default top_k initialization."""
        retriever = ConcreteRetriever()

        assert retriever.top_k == 5

    def test_initialization_custom_top_k(self):
        """Test custom top_k initialization."""
        retriever = ConcreteRetriever(top_k=10)

        assert retriever.top_k == 10

    def test_retrieve_returns_list(self):
        """Test that retrieve returns a list."""
        retriever = ConcreteRetriever()
        results = retriever.retrieve("test query")

        assert isinstance(results, list)

    def test_retrieve_respects_top_k(self):
        """Test that retrieve respects top_k limit."""
        results = [
            RetrievalResult(content=f"Content {i}", metadata={}, score=0.9 - i * 0.1, source=f"source{i}")
            for i in range(10)
        ]
        retriever = ConcreteRetriever(results=results, top_k=3)

        retrieved = retriever.retrieve("test query")

        assert len(retrieved) == 3

    def test_retrieve_with_empty_results(self):
        """Test retrieve with no results."""
        retriever = ConcreteRetriever(results=[])
        results = retriever.retrieve("test query")

        assert results == []

    def test_rerank_default_implementation(self):
        """Test that default rerank returns results unchanged."""
        original_results = [
            RetrievalResult(content="Content 1", metadata={}, score=0.9, source="source1"),
            RetrievalResult(content="Content 2", metadata={}, score=0.8, source="source2"),
        ]
        retriever = ConcreteRetriever(results=original_results)

        reranked = retriever.rerank(original_results, "test query")

        assert reranked == original_results

    def test_rerank_preserves_order(self):
        """Test that default rerank preserves original order."""
        results = [
            RetrievalResult(content=f"Content {i}", metadata={}, score=0.5, source=f"source{i}")
            for i in range(5)
        ]
        retriever = ConcreteRetriever()

        reranked = retriever.rerank(results, "query")

        for i, result in enumerate(reranked):
            assert result.content == f"Content {i}"

    def test_abstract_method_must_be_implemented(self):
        """Test that retrieve must be implemented."""

        class IncompleteRetriever(BaseRetriever):
            pass

        with pytest.raises(TypeError):
            IncompleteRetriever()


class TestBaseRetrieverWithCustomRerank:
    """Test custom rerank implementation."""

    def test_custom_rerank(self):
        """Test custom rerank implementation."""

        class CustomRerankRetriever(BaseRetriever):
            def retrieve(self, query: str) -> list[RetrievalResult]:
                return []

            def rerank(
                self,
                results: list[RetrievalResult],
                query: str,
            ) -> list[RetrievalResult]:
                # Custom rerank: reverse order
                return list(reversed(results))

        retriever = CustomRerankRetriever()
        results = [
            RetrievalResult(content="First", metadata={}, score=0.9, source="1"),
            RetrievalResult(content="Second", metadata={}, score=0.8, source="2"),
            RetrievalResult(content="Third", metadata={}, score=0.7, source="3"),
        ]

        reranked = retriever.rerank(results, "query")

        assert reranked[0].content == "Third"
        assert reranked[1].content == "Second"
        assert reranked[2].content == "First"
