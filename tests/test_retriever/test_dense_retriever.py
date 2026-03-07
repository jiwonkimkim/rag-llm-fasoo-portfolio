"""Tests for dense retriever."""

import pytest
from unittest.mock import Mock, MagicMock

from src.retriever.base_retriever import RetrievalResult
from src.retriever.dense_retriever import DenseRetriever
from src.embedder.base_embedder import BaseEmbedder
from src.vectorstore.base_store import BaseVectorStore, SearchResult


class MockEmbedder(BaseEmbedder):
    """Mock embedder for testing."""

    def __init__(self):
        super().__init__(model_name="mock-model", dimension=3)

    def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class MockVectorStore(BaseVectorStore):
    """Mock vector store for testing."""

    def __init__(self, results: list[SearchResult] | None = None):
        self.results = results or []

    def add(self, ids, embeddings, documents, metadatas=None):
        pass

    def search(self, query_embedding, top_k=5, filter=None):
        return self.results[:top_k]

    def delete(self, ids):
        pass

    def clear(self):
        pass

    def count(self):
        return len(self.results)


class TestDenseRetrieverInitialization:
    """Test cases for DenseRetriever initialization."""

    def test_initialization(self):
        """Test basic initialization."""
        embedder = MockEmbedder()
        vectorstore = MockVectorStore()

        retriever = DenseRetriever(
            embedder=embedder,
            vectorstore=vectorstore,
        )

        assert retriever.embedder == embedder
        assert retriever.vectorstore == vectorstore
        assert retriever.top_k == 5

    def test_initialization_custom_top_k(self):
        """Test initialization with custom top_k."""
        embedder = MockEmbedder()
        vectorstore = MockVectorStore()

        retriever = DenseRetriever(
            embedder=embedder,
            vectorstore=vectorstore,
            top_k=10,
        )

        assert retriever.top_k == 10


class TestDenseRetrieverRetrieve:
    """Test cases for DenseRetriever retrieve method."""

    def test_retrieve_calls_embedder(self):
        """Test that retrieve calls embedder.embed."""
        mock_embedder = Mock(spec=BaseEmbedder)
        mock_embedder.embed.return_value = [0.1, 0.2, 0.3]

        mock_vectorstore = Mock(spec=BaseVectorStore)
        mock_vectorstore.search.return_value = []

        retriever = DenseRetriever(
            embedder=mock_embedder,
            vectorstore=mock_vectorstore,
        )

        retriever.retrieve("test query")

        mock_embedder.embed.assert_called_once_with("test query")

    def test_retrieve_calls_vectorstore_search(self):
        """Test that retrieve calls vectorstore.search."""
        mock_embedder = Mock(spec=BaseEmbedder)
        mock_embedder.embed.return_value = [0.1, 0.2, 0.3]

        mock_vectorstore = Mock(spec=BaseVectorStore)
        mock_vectorstore.search.return_value = []

        retriever = DenseRetriever(
            embedder=mock_embedder,
            vectorstore=mock_vectorstore,
            top_k=3,
        )

        retriever.retrieve("test query")

        mock_vectorstore.search.assert_called_once_with(
            [0.1, 0.2, 0.3],
            top_k=3,
        )

    def test_retrieve_returns_retrieval_results(self):
        """Test that retrieve returns RetrievalResult objects."""
        embedder = MockEmbedder()
        search_results = [
            SearchResult(
                content="Document 1",
                metadata={"source": "doc1.txt"},
                score=0.95,
                id="id1",
            ),
            SearchResult(
                content="Document 2",
                metadata={"source": "doc2.txt"},
                score=0.85,
                id="id2",
            ),
        ]
        vectorstore = MockVectorStore(results=search_results)

        retriever = DenseRetriever(
            embedder=embedder,
            vectorstore=vectorstore,
        )

        results = retriever.retrieve("test query")

        assert len(results) == 2
        assert all(isinstance(r, RetrievalResult) for r in results)
        assert results[0].content == "Document 1"
        assert results[0].score == 0.95
        assert results[0].source == "doc1.txt"

    def test_retrieve_with_empty_results(self):
        """Test retrieve with no results from vectorstore."""
        embedder = MockEmbedder()
        vectorstore = MockVectorStore(results=[])

        retriever = DenseRetriever(
            embedder=embedder,
            vectorstore=vectorstore,
        )

        results = retriever.retrieve("test query")

        assert results == []

    def test_retrieve_uses_id_as_source_fallback(self):
        """Test that id is used as source when not in metadata."""
        embedder = MockEmbedder()
        search_results = [
            SearchResult(
                content="Document",
                metadata={},  # No source in metadata
                score=0.9,
                id="fallback_id",
            ),
        ]
        vectorstore = MockVectorStore(results=search_results)

        retriever = DenseRetriever(
            embedder=embedder,
            vectorstore=vectorstore,
        )

        results = retriever.retrieve("test query")

        assert results[0].source == "fallback_id"

    def test_retrieve_preserves_metadata(self):
        """Test that metadata is preserved in results."""
        embedder = MockEmbedder()
        search_results = [
            SearchResult(
                content="Document",
                metadata={
                    "source": "doc.txt",
                    "author": "Test Author",
                    "tags": ["tag1", "tag2"],
                },
                score=0.9,
                id="id1",
            ),
        ]
        vectorstore = MockVectorStore(results=search_results)

        retriever = DenseRetriever(
            embedder=embedder,
            vectorstore=vectorstore,
        )

        results = retriever.retrieve("test query")

        assert results[0].metadata["author"] == "Test Author"
        assert results[0].metadata["tags"] == ["tag1", "tag2"]


class TestDenseRetrieverRetrieveWithFilter:
    """Test cases for retrieve_with_filter method."""

    def test_retrieve_with_filter_passes_filter(self):
        """Test that filter is passed to vectorstore.search."""
        mock_embedder = Mock(spec=BaseEmbedder)
        mock_embedder.embed.return_value = [0.1, 0.2, 0.3]

        mock_vectorstore = Mock(spec=BaseVectorStore)
        mock_vectorstore.search.return_value = []

        retriever = DenseRetriever(
            embedder=mock_embedder,
            vectorstore=mock_vectorstore,
            top_k=5,
        )

        filter_dict = {"category": "technology"}
        retriever.retrieve_with_filter("test query", filter_dict)

        mock_vectorstore.search.assert_called_once_with(
            [0.1, 0.2, 0.3],
            top_k=5,
            filter=filter_dict,
        )

    def test_retrieve_with_filter_returns_results(self):
        """Test retrieve_with_filter returns filtered results."""
        embedder = MockEmbedder()

        # Create a mock vectorstore that returns different results based on filter
        mock_vectorstore = Mock(spec=BaseVectorStore)
        mock_vectorstore.search.return_value = [
            SearchResult(
                content="Filtered Document",
                metadata={"source": "filtered.txt", "category": "technology"},
                score=0.9,
                id="id1",
            ),
        ]

        retriever = DenseRetriever(
            embedder=embedder,
            vectorstore=mock_vectorstore,
        )

        results = retriever.retrieve_with_filter(
            "test query",
            {"category": "technology"},
        )

        assert len(results) == 1
        assert results[0].content == "Filtered Document"

    def test_retrieve_with_empty_filter(self):
        """Test retrieve_with_filter with empty filter."""
        mock_embedder = Mock(spec=BaseEmbedder)
        mock_embedder.embed.return_value = [0.1, 0.2, 0.3]

        mock_vectorstore = Mock(spec=BaseVectorStore)
        mock_vectorstore.search.return_value = []

        retriever = DenseRetriever(
            embedder=mock_embedder,
            vectorstore=mock_vectorstore,
        )

        retriever.retrieve_with_filter("query", {})

        mock_vectorstore.search.assert_called_once_with(
            [0.1, 0.2, 0.3],
            top_k=5,
            filter={},
        )


class TestDenseRetrieverInheritance:
    """Test inheritance from BaseRetriever."""

    def test_inherits_from_base_retriever(self):
        """Test that DenseRetriever inherits from BaseRetriever."""
        from src.retriever.base_retriever import BaseRetriever

        embedder = MockEmbedder()
        vectorstore = MockVectorStore()
        retriever = DenseRetriever(embedder=embedder, vectorstore=vectorstore)

        assert isinstance(retriever, BaseRetriever)

    def test_has_rerank_method(self):
        """Test that DenseRetriever has rerank method from base class."""
        embedder = MockEmbedder()
        vectorstore = MockVectorStore()
        retriever = DenseRetriever(embedder=embedder, vectorstore=vectorstore)

        assert hasattr(retriever, "rerank")
        assert callable(retriever.rerank)
