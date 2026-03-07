"""Tests for sparse retriever."""

import sys
import pytest
from unittest.mock import Mock, MagicMock, patch

from src.retriever.base_retriever import RetrievalResult


# Mock rank_bm25 module before importing SparseRetriever
mock_bm25_module = MagicMock()
sys.modules["rank_bm25"] = mock_bm25_module


class TestSparseRetrieverInitialization:
    """Test cases for SparseRetriever initialization."""

    def test_initialization_default(self):
        """Test default initialization."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()

        assert retriever.top_k == 5
        assert retriever.k1 == 1.5
        assert retriever.b == 0.75
        assert retriever.documents == []
        assert retriever.metadatas == []
        assert retriever.bm25 is None

    def test_initialization_custom_params(self):
        """Test initialization with custom parameters."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever(
            top_k=10,
            k1=2.0,
            b=0.5,
        )

        assert retriever.top_k == 10
        assert retriever.k1 == 2.0
        assert retriever.b == 0.5

    def test_initialization_with_documents(self):
        """Test initialization with documents."""
        from src.retriever.sparse_retriever import SparseRetriever

        mock_bm25_module.BM25Okapi.reset_mock()

        documents = ["Document one", "Document two"]
        metadatas = [{"source": "doc1"}, {"source": "doc2"}]

        retriever = SparseRetriever(
            documents=documents,
            metadatas=metadatas,
        )

        assert retriever.documents == documents
        assert retriever.metadatas == metadatas
        mock_bm25_module.BM25Okapi.assert_called_once()


class TestSparseRetrieverAddDocuments:
    """Test cases for add_documents method."""

    def test_add_documents(self):
        """Test adding documents."""
        from src.retriever.sparse_retriever import SparseRetriever

        mock_bm25_module.BM25Okapi.reset_mock()

        retriever = SparseRetriever()
        documents = ["First document", "Second document"]
        metadatas = [{"source": "first"}, {"source": "second"}]

        retriever.add_documents(documents, metadatas)

        assert retriever.documents == documents
        assert retriever.metadatas == metadatas
        mock_bm25_module.BM25Okapi.assert_called_once()

    def test_add_documents_without_metadata(self):
        """Test adding documents without metadata."""
        from src.retriever.sparse_retriever import SparseRetriever

        mock_bm25_module.BM25Okapi.reset_mock()

        retriever = SparseRetriever()
        documents = ["Document one", "Document two"]

        retriever.add_documents(documents)

        assert retriever.documents == documents
        assert retriever.metadatas == [{}, {}]

    def test_add_documents_multiple_times(self):
        """Test adding documents multiple times."""
        from src.retriever.sparse_retriever import SparseRetriever

        mock_bm25_module.BM25Okapi.reset_mock()

        retriever = SparseRetriever()

        retriever.add_documents(["Doc 1"])
        retriever.add_documents(["Doc 2", "Doc 3"])

        assert len(retriever.documents) == 3
        assert retriever.documents == ["Doc 1", "Doc 2", "Doc 3"]
        assert mock_bm25_module.BM25Okapi.call_count == 2


class TestSparseRetrieverRetrieve:
    """Test cases for retrieve method."""

    def test_retrieve_with_no_documents(self):
        """Test retrieve when no documents are added."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()
        results = retriever.retrieve("test query")

        assert results == []

    def test_retrieve_with_no_bm25(self):
        """Test retrieve when bm25 is None."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()
        retriever.documents = ["doc"]  # Has documents but no bm25
        retriever.bm25 = None

        results = retriever.retrieve("test query")

        assert results == []

    def test_retrieve_returns_results(self):
        """Test retrieve returns results."""
        from src.retriever.sparse_retriever import SparseRetriever

        mock_bm25 = MagicMock()
        mock_bm25.get_scores.return_value = [0.8, 0.6, 0.9]
        mock_bm25_module.BM25Okapi.return_value = mock_bm25

        retriever = SparseRetriever()
        retriever.documents = ["Doc 1", "Doc 2", "Doc 3"]
        retriever.metadatas = [
            {"source": "source1"},
            {"source": "source2"},
            {"source": "source3"},
        ]
        retriever.bm25 = mock_bm25

        results = retriever.retrieve("test query")

        # Should return sorted by score (highest first)
        assert len(results) > 0
        assert all(isinstance(r, RetrievalResult) for r in results)

    def test_retrieve_respects_top_k(self):
        """Test retrieve respects top_k limit."""
        from src.retriever.sparse_retriever import SparseRetriever

        mock_bm25 = MagicMock()
        mock_bm25.get_scores.return_value = [0.8, 0.6, 0.9, 0.7, 0.5]
        mock_bm25_module.BM25Okapi.return_value = mock_bm25

        retriever = SparseRetriever(top_k=2)
        retriever.documents = ["Doc 1", "Doc 2", "Doc 3", "Doc 4", "Doc 5"]
        retriever.metadatas = [{"source": f"source{i}"} for i in range(5)]
        retriever.bm25 = mock_bm25

        results = retriever.retrieve("test query")

        assert len(results) <= 2

    def test_retrieve_excludes_zero_scores(self):
        """Test retrieve excludes results with zero score."""
        from src.retriever.sparse_retriever import SparseRetriever

        mock_bm25 = MagicMock()
        mock_bm25.get_scores.return_value = [0.8, 0.0, 0.0]  # Two zero scores
        mock_bm25_module.BM25Okapi.return_value = mock_bm25

        retriever = SparseRetriever(top_k=5)
        retriever.documents = ["Doc 1", "Doc 2", "Doc 3"]
        retriever.metadatas = [{"source": f"source{i}"} for i in range(3)]
        retriever.bm25 = mock_bm25

        results = retriever.retrieve("test query")

        # Only one result with positive score
        assert len(results) == 1
        assert results[0].score == 0.8

    def test_retrieve_uses_doc_index_as_fallback_source(self):
        """Test retrieve uses doc_idx as source when not in metadata."""
        from src.retriever.sparse_retriever import SparseRetriever

        mock_bm25 = MagicMock()
        mock_bm25.get_scores.return_value = [0.8]
        mock_bm25_module.BM25Okapi.return_value = mock_bm25

        retriever = SparseRetriever()
        retriever.documents = ["Document"]
        retriever.metadatas = [{}]  # No source in metadata
        retriever.bm25 = mock_bm25

        results = retriever.retrieve("query")

        assert results[0].source == "doc_0"


class TestSparseRetrieverTokenize:
    """Test cases for _tokenize method."""

    def test_tokenize_lowercase(self):
        """Test tokenization converts to lowercase."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()
        tokens = retriever._tokenize("Hello WORLD")

        assert "hello" in tokens
        assert "world" in tokens
        assert "Hello" not in tokens
        assert "WORLD" not in tokens

    def test_tokenize_word_extraction(self):
        """Test tokenization extracts words."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()
        tokens = retriever._tokenize("Hello, world! How are you?")

        assert "hello" in tokens
        assert "world" in tokens
        assert "how" in tokens
        assert "are" in tokens
        assert "you" in tokens
        assert "," not in tokens
        assert "!" not in tokens

    def test_tokenize_numbers(self):
        """Test tokenization handles numbers."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()
        tokens = retriever._tokenize("The price is 100 dollars")

        assert "100" in tokens
        assert "price" in tokens
        assert "dollars" in tokens

    def test_tokenize_empty_string(self):
        """Test tokenization of empty string."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()
        tokens = retriever._tokenize("")

        assert tokens == []


class TestSparseRetrieverInheritance:
    """Test inheritance from BaseRetriever."""

    def test_inherits_from_base_retriever(self):
        """Test that SparseRetriever inherits from BaseRetriever."""
        from src.retriever.base_retriever import BaseRetriever
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()

        assert isinstance(retriever, BaseRetriever)

    def test_has_rerank_method(self):
        """Test that SparseRetriever has rerank method."""
        from src.retriever.sparse_retriever import SparseRetriever

        retriever = SparseRetriever()

        assert hasattr(retriever, "rerank")
        assert callable(retriever.rerank)
