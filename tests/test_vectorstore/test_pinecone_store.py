"""Tests for Pinecone vector store."""

import sys
import pytest
from unittest.mock import MagicMock, Mock


# Mock pinecone module before importing PineconeStore
mock_pinecone_module = MagicMock()
sys.modules["pinecone"] = mock_pinecone_module


class TestPineconeStoreInitialization:
    """Test cases for PineconeStore initialization."""

    def test_initialization_default(self):
        """Test default initialization."""
        mock_pinecone_module.reset_mock()
        mock_pc = MagicMock()
        mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = mock_pc
        mock_pc.Index.return_value = mock_index

        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index")

        mock_pinecone_module.Pinecone.assert_called_once_with(api_key=None)
        mock_pc.Index.assert_called_once_with("test-index")
        assert store.namespace == ""

    def test_initialization_with_api_key(self):
        """Test initialization with API key."""
        mock_pinecone_module.reset_mock()
        mock_pc = MagicMock()
        mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = mock_pc
        mock_pc.Index.return_value = mock_index

        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(
            index_name="test-index",
            api_key="test-api-key",
        )

        mock_pinecone_module.Pinecone.assert_called_once_with(api_key="test-api-key")

    def test_initialization_with_namespace(self):
        """Test initialization with namespace."""
        mock_pinecone_module.reset_mock()
        mock_pc = MagicMock()
        mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = mock_pc
        mock_pc.Index.return_value = mock_index

        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(
            index_name="test-index",
            namespace="test-namespace",
        )

        assert store.namespace == "test-namespace"

    def test_initialization_with_environment(self):
        """Test initialization with environment parameter."""
        mock_pinecone_module.reset_mock()
        mock_pc = MagicMock()
        mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = mock_pc
        mock_pc.Index.return_value = mock_index

        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(
            index_name="test-index",
            environment="us-west1-gcp",
        )

        # Environment is stored but default is "gcp-starter"
        mock_pinecone_module.Pinecone.assert_called_once()


class TestPineconeStoreAdd:
    """Test cases for add method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_pinecone_module.reset_mock()
        self.mock_pc = MagicMock()
        self.mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = self.mock_pc
        self.mock_pc.Index.return_value = self.mock_index

    def test_add_documents(self):
        """Test adding documents."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index")

        store.add(
            ids=["id1", "id2"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["Doc 1", "Doc 2"],
            metadatas=[{"key": "val1"}, {"key": "val2"}],
        )

        self.mock_index.upsert.assert_called_once()
        call_args = self.mock_index.upsert.call_args
        vectors = call_args.kwargs["vectors"]

        assert len(vectors) == 2
        assert vectors[0]["id"] == "id1"
        assert vectors[0]["values"] == [0.1, 0.2]
        assert vectors[0]["metadata"]["text"] == "Doc 1"
        assert vectors[0]["metadata"]["key"] == "val1"

    def test_add_documents_without_metadata(self):
        """Test adding documents without metadata."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index")

        store.add(
            ids=["id1"],
            embeddings=[[0.1, 0.2]],
            documents=["Doc 1"],
        )

        self.mock_index.upsert.assert_called_once()
        call_args = self.mock_index.upsert.call_args
        vectors = call_args.kwargs["vectors"]

        assert vectors[0]["metadata"]["text"] == "Doc 1"

    def test_add_with_namespace(self):
        """Test adding documents with namespace."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index", namespace="test-ns")

        store.add(
            ids=["id1"],
            embeddings=[[0.1, 0.2]],
            documents=["Doc 1"],
        )

        call_args = self.mock_index.upsert.call_args
        assert call_args.kwargs["namespace"] == "test-ns"

    def test_add_batch_processing(self):
        """Test that large batches are split."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index")

        # Add more than 100 documents to trigger batching
        ids = [f"id{i}" for i in range(150)]
        embeddings = [[0.1, 0.2] for _ in range(150)]
        documents = [f"Doc {i}" for i in range(150)]

        store.add(ids=ids, embeddings=embeddings, documents=documents)

        # Should be called twice (100 + 50)
        assert self.mock_index.upsert.call_count == 2


class TestPineconeStoreSearch:
    """Test cases for search method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_pinecone_module.reset_mock()
        self.mock_pc = MagicMock()
        self.mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = self.mock_pc
        self.mock_pc.Index.return_value = self.mock_index

    def test_search_returns_results(self):
        """Test search returns SearchResult objects."""
        from src.vectorstore.pinecone_store import PineconeStore
        from src.vectorstore.base_store import SearchResult

        # Mock query results
        mock_match1 = MagicMock()
        mock_match1.id = "id1"
        mock_match1.score = 0.95
        mock_match1.metadata = {"text": "Doc 1", "source": "a"}

        mock_match2 = MagicMock()
        mock_match2.id = "id2"
        mock_match2.score = 0.85
        mock_match2.metadata = {"text": "Doc 2", "source": "b"}

        mock_results = MagicMock()
        mock_results.matches = [mock_match1, mock_match2]
        self.mock_index.query.return_value = mock_results

        store = PineconeStore(index_name="test-index")
        results = store.search([0.1, 0.2], top_k=5)

        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].content == "Doc 1"
        assert results[0].score == 0.95
        assert results[0].id == "id1"
        # "text" should be removed from metadata
        assert "text" not in results[0].metadata
        assert results[0].metadata["source"] == "a"

    def test_search_with_filter(self):
        """Test search with filter parameter."""
        from src.vectorstore.pinecone_store import PineconeStore

        mock_results = MagicMock()
        mock_results.matches = []
        self.mock_index.query.return_value = mock_results

        store = PineconeStore(index_name="test-index")
        store.search([0.1, 0.2], top_k=5, filter={"category": "tech"})

        self.mock_index.query.assert_called_once_with(
            vector=[0.1, 0.2],
            top_k=5,
            filter={"category": "tech"},
            include_metadata=True,
            namespace="",
        )

    def test_search_with_namespace(self):
        """Test search uses correct namespace."""
        from src.vectorstore.pinecone_store import PineconeStore

        mock_results = MagicMock()
        mock_results.matches = []
        self.mock_index.query.return_value = mock_results

        store = PineconeStore(index_name="test-index", namespace="test-ns")
        store.search([0.1, 0.2])

        call_args = self.mock_index.query.call_args
        assert call_args.kwargs["namespace"] == "test-ns"

    def test_search_empty_results(self):
        """Test search with no results."""
        from src.vectorstore.pinecone_store import PineconeStore

        mock_results = MagicMock()
        mock_results.matches = []
        self.mock_index.query.return_value = mock_results

        store = PineconeStore(index_name="test-index")
        results = store.search([0.1, 0.2])

        assert results == []

    def test_search_handles_none_metadata(self):
        """Test search handles None metadata."""
        from src.vectorstore.pinecone_store import PineconeStore

        mock_match = MagicMock()
        mock_match.id = "id1"
        mock_match.score = 0.9
        mock_match.metadata = None

        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        self.mock_index.query.return_value = mock_results

        store = PineconeStore(index_name="test-index")
        results = store.search([0.1, 0.2])

        assert len(results) == 1
        assert results[0].content == ""
        assert results[0].metadata == {}


class TestPineconeStoreDelete:
    """Test cases for delete method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_pinecone_module.reset_mock()
        self.mock_pc = MagicMock()
        self.mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = self.mock_pc
        self.mock_pc.Index.return_value = self.mock_index

    def test_delete_documents(self):
        """Test deleting documents by IDs."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index")
        store.delete(["id1", "id2"])

        self.mock_index.delete.assert_called_once_with(
            ids=["id1", "id2"],
            namespace="",
        )

    def test_delete_with_namespace(self):
        """Test deleting documents with namespace."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index", namespace="test-ns")
        store.delete(["id1"])

        self.mock_index.delete.assert_called_once_with(
            ids=["id1"],
            namespace="test-ns",
        )


class TestPineconeStoreClear:
    """Test cases for clear method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_pinecone_module.reset_mock()
        self.mock_pc = MagicMock()
        self.mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = self.mock_pc
        self.mock_pc.Index.return_value = self.mock_index

    def test_clear_deletes_all(self):
        """Test clear deletes all vectors in namespace."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index")
        store.clear()

        self.mock_index.delete.assert_called_once_with(
            delete_all=True,
            namespace="",
        )

    def test_clear_with_namespace(self):
        """Test clear with namespace."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index", namespace="test-ns")
        store.clear()

        self.mock_index.delete.assert_called_once_with(
            delete_all=True,
            namespace="test-ns",
        )


class TestPineconeStoreCount:
    """Test cases for count method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_pinecone_module.reset_mock()
        self.mock_pc = MagicMock()
        self.mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = self.mock_pc
        self.mock_pc.Index.return_value = self.mock_index

    def test_count_without_namespace(self):
        """Test count returns total vector count."""
        from src.vectorstore.pinecone_store import PineconeStore

        mock_stats = MagicMock()
        mock_stats.total_vector_count = 100
        self.mock_index.describe_index_stats.return_value = mock_stats

        store = PineconeStore(index_name="test-index")
        count = store.count()

        assert count == 100
        self.mock_index.describe_index_stats.assert_called_once()

    def test_count_with_namespace(self):
        """Test count returns namespace vector count."""
        from src.vectorstore.pinecone_store import PineconeStore

        mock_stats = MagicMock()
        mock_stats.namespaces = {"test-ns": {"vector_count": 50}}
        self.mock_index.describe_index_stats.return_value = mock_stats

        store = PineconeStore(index_name="test-index", namespace="test-ns")
        count = store.count()

        assert count == 50

    def test_count_with_nonexistent_namespace(self):
        """Test count returns 0 for nonexistent namespace."""
        from src.vectorstore.pinecone_store import PineconeStore

        mock_stats = MagicMock()
        mock_stats.namespaces = {}
        self.mock_index.describe_index_stats.return_value = mock_stats

        store = PineconeStore(index_name="test-index", namespace="nonexistent")
        count = store.count()

        assert count == 0


class TestPineconeStoreInheritance:
    """Test inheritance from BaseVectorStore."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_pinecone_module.reset_mock()
        self.mock_pc = MagicMock()
        self.mock_index = MagicMock()
        mock_pinecone_module.Pinecone.return_value = self.mock_pc
        self.mock_pc.Index.return_value = self.mock_index

    def test_inherits_from_base_vector_store(self):
        """Test that PineconeStore inherits from BaseVectorStore."""
        from src.vectorstore.base_store import BaseVectorStore
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index")

        assert isinstance(store, BaseVectorStore)

    def test_has_required_methods(self):
        """Test that PineconeStore has all required methods."""
        from src.vectorstore.pinecone_store import PineconeStore

        store = PineconeStore(index_name="test-index")

        assert hasattr(store, "add")
        assert hasattr(store, "search")
        assert hasattr(store, "delete")
        assert hasattr(store, "clear")
        assert hasattr(store, "count")
