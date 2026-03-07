"""Tests for ChromaDB vector store."""

import sys
import pytest
from unittest.mock import MagicMock, Mock


# Mock chromadb module before importing ChromaStore
mock_chromadb_module = MagicMock()
sys.modules["chromadb"] = mock_chromadb_module


class TestChromaStoreInitialization:
    """Test cases for ChromaStore initialization."""

    def test_initialization_in_memory(self):
        """Test default initialization (in-memory)."""
        mock_chromadb_module.reset_mock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb_module.Client.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from src.vectorstore.chroma_store import ChromaStore

        store = ChromaStore(collection_name="test_collection")

        mock_chromadb_module.Client.assert_called_once()
        mock_client.get_or_create_collection.assert_called_once_with(
            name="test_collection",
            metadata={"hnsw:space": "cosine"},
        )
        assert store.collection == mock_collection

    def test_initialization_persistent(self):
        """Test initialization with persist directory."""
        mock_chromadb_module.reset_mock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb_module.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from src.vectorstore.chroma_store import ChromaStore

        store = ChromaStore(
            collection_name="persistent_collection",
            persist_directory="/path/to/db",
        )

        mock_chromadb_module.PersistentClient.assert_called_once_with(path="/path/to/db")
        mock_client.get_or_create_collection.assert_called_once()

    def test_initialization_default_collection_name(self):
        """Test default collection name is 'rag_collection'."""
        mock_chromadb_module.reset_mock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb_module.Client.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from src.vectorstore.chroma_store import ChromaStore

        store = ChromaStore()

        mock_client.get_or_create_collection.assert_called_once_with(
            name="rag_collection",
            metadata={"hnsw:space": "cosine"},
        )


class TestChromaStoreAdd:
    """Test cases for add method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_chromadb_module.reset_mock()
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        mock_chromadb_module.Client.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def test_add_documents(self):
        """Test adding documents to collection."""
        from src.vectorstore.chroma_store import ChromaStore

        store = ChromaStore()

        store.add(
            ids=["id1", "id2"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["Doc 1", "Doc 2"],
            metadatas=[{"key": "val1"}, {"key": "val2"}],
        )

        self.mock_collection.add.assert_called_once_with(
            ids=["id1", "id2"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["Doc 1", "Doc 2"],
            metadatas=[{"key": "val1"}, {"key": "val2"}],
        )

    def test_add_documents_without_metadata(self):
        """Test adding documents without metadata."""
        from src.vectorstore.chroma_store import ChromaStore

        store = ChromaStore()

        store.add(
            ids=["id1"],
            embeddings=[[0.1, 0.2]],
            documents=["Doc 1"],
        )

        self.mock_collection.add.assert_called_once_with(
            ids=["id1"],
            embeddings=[[0.1, 0.2]],
            documents=["Doc 1"],
            metadatas=None,
        )


class TestChromaStoreSearch:
    """Test cases for search method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_chromadb_module.reset_mock()
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        mock_chromadb_module.Client.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def test_search_returns_results(self):
        """Test search returns SearchResult objects."""
        from src.vectorstore.chroma_store import ChromaStore
        from src.vectorstore.base_store import SearchResult

        self.mock_collection.query.return_value = {
            "ids": [["id1", "id2"]],
            "documents": [["Doc 1", "Doc 2"]],
            "metadatas": [[{"source": "a"}, {"source": "b"}]],
            "distances": [[0.1, 0.2]],
        }

        store = ChromaStore()
        results = store.search([0.1, 0.2], top_k=5)

        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].content == "Doc 1"
        assert results[0].id == "id1"
        # Score is 1 - distance
        assert results[0].score == 0.9

    def test_search_with_filter(self):
        """Test search with filter parameter."""
        from src.vectorstore.chroma_store import ChromaStore

        self.mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        store = ChromaStore()
        store.search([0.1, 0.2], top_k=5, filter={"category": "tech"})

        self.mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2]],
            n_results=5,
            where={"category": "tech"},
            include=["documents", "metadatas", "distances"],
        )

    def test_search_empty_results(self):
        """Test search with no results."""
        from src.vectorstore.chroma_store import ChromaStore

        self.mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        store = ChromaStore()
        results = store.search([0.1, 0.2])

        assert results == []

    def test_search_handles_none_fields(self):
        """Test search handles None in result fields."""
        from src.vectorstore.chroma_store import ChromaStore

        self.mock_collection.query.return_value = {
            "ids": [["id1"]],
            "documents": None,
            "metadatas": None,
            "distances": None,
        }

        store = ChromaStore()
        results = store.search([0.1, 0.2])

        assert len(results) == 1
        assert results[0].content == ""
        assert results[0].metadata == {}
        assert results[0].score == 0


class TestChromaStoreDelete:
    """Test cases for delete method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_chromadb_module.reset_mock()
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        mock_chromadb_module.Client.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def test_delete_documents(self):
        """Test deleting documents by IDs."""
        from src.vectorstore.chroma_store import ChromaStore

        store = ChromaStore()
        store.delete(["id1", "id2"])

        self.mock_collection.delete.assert_called_once_with(ids=["id1", "id2"])


class TestChromaStoreClear:
    """Test cases for clear method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_chromadb_module.reset_mock()
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_collection.name = "test_collection"
        mock_chromadb_module.Client.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def test_clear_deletes_and_recreates_collection(self):
        """Test clear deletes and recreates collection."""
        from src.vectorstore.chroma_store import ChromaStore

        new_collection = MagicMock()
        self.mock_client.create_collection.return_value = new_collection

        store = ChromaStore(collection_name="test_collection")
        store.clear()

        self.mock_client.delete_collection.assert_called_once_with("test_collection")
        self.mock_client.create_collection.assert_called_once_with(
            name="test_collection",
            metadata={"hnsw:space": "cosine"},
        )
        assert store.collection == new_collection


class TestChromaStoreCount:
    """Test cases for count method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_chromadb_module.reset_mock()
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        mock_chromadb_module.Client.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def test_count_returns_collection_count(self):
        """Test count returns collection count."""
        from src.vectorstore.chroma_store import ChromaStore

        self.mock_collection.count.return_value = 42

        store = ChromaStore()
        count = store.count()

        assert count == 42
        self.mock_collection.count.assert_called_once()


class TestChromaStoreInheritance:
    """Test inheritance from BaseVectorStore."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_chromadb_module.reset_mock()
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        mock_chromadb_module.Client.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def test_inherits_from_base_vector_store(self):
        """Test that ChromaStore inherits from BaseVectorStore."""
        from src.vectorstore.base_store import BaseVectorStore
        from src.vectorstore.chroma_store import ChromaStore

        store = ChromaStore()

        assert isinstance(store, BaseVectorStore)

    def test_has_required_methods(self):
        """Test that ChromaStore has all required methods."""
        from src.vectorstore.chroma_store import ChromaStore

        store = ChromaStore()

        assert hasattr(store, "add")
        assert hasattr(store, "search")
        assert hasattr(store, "delete")
        assert hasattr(store, "clear")
        assert hasattr(store, "count")
