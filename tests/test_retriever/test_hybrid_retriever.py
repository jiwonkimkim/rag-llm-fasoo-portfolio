"""Tests for hybrid retriever."""

import pytest
from unittest.mock import Mock, MagicMock

from src.retriever.base_retriever import RetrievalResult
from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.dense_retriever import DenseRetriever
from src.retriever.sparse_retriever import SparseRetriever


def create_mock_dense_retriever(results: list[RetrievalResult] | None = None):
    """Create a mock dense retriever."""
    mock = Mock(spec=DenseRetriever)
    mock.retrieve.return_value = results or []
    return mock


def create_mock_sparse_retriever(results: list[RetrievalResult] | None = None):
    """Create a mock sparse retriever."""
    mock = Mock(spec=SparseRetriever)
    mock.retrieve.return_value = results or []
    return mock


class TestHybridRetrieverInitialization:
    """Test cases for HybridRetriever initialization."""

    def test_initialization_default(self):
        """Test default initialization."""
        dense = create_mock_dense_retriever()
        sparse = create_mock_sparse_retriever()

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        assert retriever.dense_retriever == dense
        assert retriever.sparse_retriever == sparse
        assert retriever.top_k == 5
        assert retriever.dense_weight == 0.5
        assert retriever.sparse_weight == 0.5

    def test_initialization_custom_params(self):
        """Test initialization with custom parameters."""
        dense = create_mock_dense_retriever()
        sparse = create_mock_sparse_retriever()

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
            top_k=10,
            dense_weight=0.7,
            sparse_weight=0.3,
        )

        assert retriever.top_k == 10
        assert retriever.dense_weight == 0.7
        assert retriever.sparse_weight == 0.3


class TestHybridRetrieverRetrieve:
    """Test cases for retrieve method."""

    def test_retrieve_calls_both_retrievers(self):
        """Test that retrieve calls both dense and sparse retrievers."""
        dense = create_mock_dense_retriever()
        sparse = create_mock_sparse_retriever()

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        retriever.retrieve("test query")

        dense.retrieve.assert_called_once_with("test query")
        sparse.retrieve.assert_called_once_with("test query")

    def test_retrieve_returns_retrieval_results(self):
        """Test that retrieve returns RetrievalResult objects."""
        dense_results = [
            RetrievalResult(content="Dense 1", metadata={}, score=0.9, source="dense1"),
        ]
        sparse_results = [
            RetrievalResult(content="Sparse 1", metadata={}, score=0.8, source="sparse1"),
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever(sparse_results)

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        results = retriever.retrieve("test query")

        assert all(isinstance(r, RetrievalResult) for r in results)

    def test_retrieve_combines_results(self):
        """Test that retrieve combines results from both retrievers."""
        dense_results = [
            RetrievalResult(content="Document A", metadata={}, score=0.9, source="a"),
        ]
        sparse_results = [
            RetrievalResult(content="Document B", metadata={}, score=0.8, source="b"),
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever(sparse_results)

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        results = retriever.retrieve("test query")

        contents = [r.content for r in results]
        assert "Document A" in contents
        assert "Document B" in contents

    def test_retrieve_with_empty_dense_results(self):
        """Test retrieve when dense retriever returns empty."""
        sparse_results = [
            RetrievalResult(content="Sparse only", metadata={}, score=0.8, source="sparse"),
        ]

        dense = create_mock_dense_retriever([])
        sparse = create_mock_sparse_retriever(sparse_results)

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        results = retriever.retrieve("test query")

        assert len(results) == 1
        assert results[0].content == "Sparse only"

    def test_retrieve_with_empty_sparse_results(self):
        """Test retrieve when sparse retriever returns empty."""
        dense_results = [
            RetrievalResult(content="Dense only", metadata={}, score=0.9, source="dense"),
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever([])

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        results = retriever.retrieve("test query")

        assert len(results) == 1
        assert results[0].content == "Dense only"

    def test_retrieve_with_both_empty(self):
        """Test retrieve when both retrievers return empty."""
        dense = create_mock_dense_retriever([])
        sparse = create_mock_sparse_retriever([])

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        results = retriever.retrieve("test query")

        assert results == []

    def test_retrieve_respects_top_k(self):
        """Test that retrieve respects top_k limit."""
        dense_results = [
            RetrievalResult(content=f"Dense {i}", metadata={}, score=0.9 - i * 0.1, source=f"d{i}")
            for i in range(5)
        ]
        sparse_results = [
            RetrievalResult(content=f"Sparse {i}", metadata={}, score=0.85 - i * 0.1, source=f"s{i}")
            for i in range(5)
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever(sparse_results)

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
            top_k=3,
        )

        results = retriever.retrieve("test query")

        assert len(results) == 3

    def test_retrieve_deduplicates_by_content(self):
        """Test that duplicate content is deduplicated."""
        # Same content in both results
        dense_results = [
            RetrievalResult(content="Same Document", metadata={"from": "dense"}, score=0.9, source="dense"),
        ]
        sparse_results = [
            RetrievalResult(content="Same Document", metadata={"from": "sparse"}, score=0.8, source="sparse"),
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever(sparse_results)

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        results = retriever.retrieve("test query")

        # Should only have one result since content is the same
        assert len(results) == 1
        assert results[0].content == "Same Document"


class TestHybridRetrieverRRF:
    """Test cases for Reciprocal Rank Fusion."""

    def test_rrf_scoring(self):
        """Test RRF scoring calculation."""
        dense_results = [
            RetrievalResult(content="Doc 1", metadata={}, score=0.9, source="d1"),
            RetrievalResult(content="Doc 2", metadata={}, score=0.8, source="d2"),
        ]
        sparse_results = [
            RetrievalResult(content="Doc 2", metadata={}, score=0.85, source="s2"),
            RetrievalResult(content="Doc 3", metadata={}, score=0.7, source="s3"),
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever(sparse_results)

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
            dense_weight=0.5,
            sparse_weight=0.5,
        )

        results = retriever.retrieve("test query")

        # Doc 2 appears in both, so should have higher combined score
        contents = [r.content for r in results]
        doc2_idx = contents.index("Doc 2")

        # Doc 2 should be ranked highly due to appearing in both
        assert doc2_idx <= 1  # Should be in top 2

    def test_rrf_with_different_weights(self):
        """Test RRF with different weights for dense and sparse."""
        dense_results = [
            RetrievalResult(content="Dense First", metadata={}, score=0.9, source="d1"),
        ]
        sparse_results = [
            RetrievalResult(content="Sparse First", metadata={}, score=0.9, source="s1"),
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever(sparse_results)

        # Higher weight for dense
        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
            dense_weight=0.8,
            sparse_weight=0.2,
        )

        results = retriever.retrieve("test query")

        # Dense result should be first due to higher weight
        assert results[0].content == "Dense First"


class TestHybridRetrieverRetrieveWithRerank:
    """Test cases for retrieve_with_rerank method."""

    def test_retrieve_with_rerank_no_reranker(self):
        """Test retrieve_with_rerank without a reranker."""
        dense_results = [
            RetrievalResult(content="Doc", metadata={}, score=0.9, source="d"),
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever([])

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        results = retriever.retrieve_with_rerank("query", reranker=None)

        assert len(results) == 1
        assert results[0].content == "Doc"

    def test_retrieve_with_rerank_calls_rerank(self):
        """Test retrieve_with_rerank calls rerank when reranker provided."""
        dense_results = [
            RetrievalResult(content="Doc", metadata={}, score=0.9, source="d"),
        ]

        dense = create_mock_dense_retriever(dense_results)
        sparse = create_mock_sparse_retriever([])

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        # Mock reranker (truthy value)
        mock_reranker = Mock()

        # Need to mock the rerank method to verify it's called
        original_rerank = retriever.rerank
        retriever.rerank = Mock(side_effect=original_rerank)

        retriever.retrieve_with_rerank("query", reranker=mock_reranker)

        retriever.rerank.assert_called_once()


class TestHybridRetrieverInheritance:
    """Test inheritance from BaseRetriever."""

    def test_inherits_from_base_retriever(self):
        """Test that HybridRetriever inherits from BaseRetriever."""
        from src.retriever.base_retriever import BaseRetriever

        dense = create_mock_dense_retriever()
        sparse = create_mock_sparse_retriever()

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        assert isinstance(retriever, BaseRetriever)

    def test_has_base_retriever_attributes(self):
        """Test that HybridRetriever has base retriever attributes."""
        dense = create_mock_dense_retriever()
        sparse = create_mock_sparse_retriever()

        retriever = HybridRetriever(
            dense_retriever=dense,
            sparse_retriever=sparse,
        )

        assert hasattr(retriever, "top_k")
        assert hasattr(retriever, "retrieve")
        assert hasattr(retriever, "rerank")
