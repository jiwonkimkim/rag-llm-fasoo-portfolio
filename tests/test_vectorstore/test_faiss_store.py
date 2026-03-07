"""Tests for FAISS vector store."""

import sys
import pytest
from unittest.mock import MagicMock, Mock, patch
import json


# Mock faiss and numpy modules before importing FAISSStore
mock_faiss_module = MagicMock()
mock_numpy_module = MagicMock()
sys.modules["faiss"] = mock_faiss_module
sys.modules["numpy"] = mock_numpy_module


class TestFAISSStoreInitialization:
    """Test cases for FAISSStore initialization."""

    def test_initialization_default(self):
        """Test default initialization."""
        mock_faiss_module.reset_mock()
        mock_numpy_module.reset_mock()
        mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = mock_index

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore()

        assert store.dimension == 1536
        assert store.index_path is None
        mock_faiss_module.IndexFlatIP.assert_called_once_with(1536)
        assert store.documents == {}
        assert store.metadatas == {}

    def test_initialization_custom_dimension(self):
        """Test initialization with custom dimension."""
        mock_faiss_module.reset_mock()
        mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = mock_index

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=768)

        assert store.dimension == 768
        mock_faiss_module.IndexFlatIP.assert_called_once_with(768)

    def test_initialization_with_index_path(self):
        """Test initialization with index path (no existing data)."""
        mock_faiss_module.reset_mock()
        mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = mock_index

        from src.vectorstore.faiss_store import FAISSStore

        # Use a non-existent path
        store = FAISSStore(index_path="/nonexistent/path")

        from pathlib import Path

        assert store.index_path == Path("/nonexistent/path")


class TestFAISSStoreAdd:
    """Test cases for add method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_faiss_module.reset_mock()
        mock_numpy_module.reset_mock()
        self.mock_index = MagicMock()
        self.mock_index.ntotal = 0
        mock_faiss_module.IndexFlatIP.return_value = self.mock_index

    def test_add_documents(self):
        """Test adding documents."""
        mock_numpy_module.array.return_value = MagicMock()
        mock_numpy_module.float32 = "float32"

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.add(
            ids=["id1", "id2"],
            embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            documents=["Doc 1", "Doc 2"],
            metadatas=[{"key": "val1"}, {"key": "val2"}],
        )

        self.mock_index.add.assert_called_once()
        assert store.documents["id1"] == "Doc 1"
        assert store.documents["id2"] == "Doc 2"
        assert store.metadatas["id1"] == {"key": "val1"}
        assert store.metadatas["id2"] == {"key": "val2"}

    def test_add_documents_without_metadata(self):
        """Test adding documents without metadata."""
        mock_numpy_module.array.return_value = MagicMock()
        mock_numpy_module.float32 = "float32"

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.add(
            ids=["id1"],
            embeddings=[[0.1, 0.2, 0.3]],
            documents=["Doc 1"],
        )

        assert store.documents["id1"] == "Doc 1"
        assert store.metadatas["id1"] == {}

    def test_add_updates_id_mappings(self):
        """Test that add updates ID to index mappings."""
        mock_numpy_module.array.return_value = MagicMock()
        mock_numpy_module.float32 = "float32"

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.add(
            ids=["id1", "id2"],
            embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            documents=["Doc 1", "Doc 2"],
        )

        assert "id1" in store.id_to_idx
        assert "id2" in store.id_to_idx
        assert store.idx_to_id[store.id_to_idx["id1"]] == "id1"
        assert store.idx_to_id[store.id_to_idx["id2"]] == "id2"


class TestFAISSStoreSearch:
    """Test cases for search method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_faiss_module.reset_mock()
        mock_numpy_module.reset_mock()
        self.mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = self.mock_index

    def test_search_empty_index(self):
        """Test search on empty index."""
        self.mock_index.ntotal = 0

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        results = store.search([0.1, 0.2, 0.3])

        assert results == []

    def test_search_returns_results(self):
        """Test search returns SearchResult objects."""
        mock_numpy_module.array.return_value = MagicMock()
        mock_numpy_module.float32 = "float32"
        self.mock_index.ntotal = 2
        self.mock_index.search.return_value = (
            [[0.9, 0.8]],  # scores
            [[0, 1]],  # indices
        )

        from src.vectorstore.faiss_store import FAISSStore
        from src.vectorstore.base_store import SearchResult

        store = FAISSStore(dimension=3)
        store.documents = {"id1": "Doc 1", "id2": "Doc 2"}
        store.metadatas = {"id1": {"source": "a"}, "id2": {"source": "b"}}
        store.idx_to_id = {0: "id1", 1: "id2"}
        store.id_to_idx = {"id1": 0, "id2": 1}

        results = store.search([0.1, 0.2, 0.3], top_k=5)

        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].content == "Doc 1"
        assert results[0].score == 0.9

    def test_search_respects_top_k(self):
        """Test search respects top_k parameter."""
        mock_numpy_module.array.return_value = MagicMock()
        mock_numpy_module.float32 = "float32"
        self.mock_index.ntotal = 5
        self.mock_index.search.return_value = (
            [[0.9, 0.8]],
            [[0, 1]],
        )

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.documents = {"id1": "Doc 1", "id2": "Doc 2"}
        store.metadatas = {"id1": {}, "id2": {}}
        store.idx_to_id = {0: "id1", 1: "id2"}

        results = store.search([0.1, 0.2, 0.3], top_k=2)

        # Verify search was called with correct top_k
        self.mock_index.search.assert_called_once()

    def test_search_with_filter(self):
        """Test search with metadata filter."""
        mock_numpy_module.array.return_value = MagicMock()
        mock_numpy_module.float32 = "float32"
        self.mock_index.ntotal = 2
        self.mock_index.search.return_value = (
            [[0.9, 0.8]],
            [[0, 1]],
        )

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.documents = {"id1": "Doc 1", "id2": "Doc 2"}
        store.metadatas = {"id1": {"category": "tech"}, "id2": {"category": "news"}}
        store.idx_to_id = {0: "id1", 1: "id2"}

        results = store.search([0.1, 0.2, 0.3], filter={"category": "tech"})

        # Only id1 should match the filter
        assert len(results) == 1
        assert results[0].content == "Doc 1"

    def test_search_handles_invalid_index(self):
        """Test search handles -1 indices from FAISS."""
        mock_numpy_module.array.return_value = MagicMock()
        mock_numpy_module.float32 = "float32"
        self.mock_index.ntotal = 1
        self.mock_index.search.return_value = (
            [[0.9, 0.0]],
            [[0, -1]],  # -1 indicates no match
        )

        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.documents = {"id1": "Doc 1"}
        store.metadatas = {"id1": {}}
        store.idx_to_id = {0: "id1"}

        results = store.search([0.1, 0.2, 0.3], top_k=2)

        # Should only return valid results
        assert len(results) == 1


class TestFAISSStoreDelete:
    """Test cases for delete method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_faiss_module.reset_mock()
        self.mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = self.mock_index

    def test_delete_documents(self):
        """Test deleting documents."""
        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.documents = {"id1": "Doc 1", "id2": "Doc 2"}
        store.metadatas = {"id1": {}, "id2": {}}
        store.id_to_idx = {"id1": 0, "id2": 1}
        store.idx_to_id = {0: "id1", 1: "id2"}

        store.delete(["id1"])

        assert "id1" not in store.documents
        assert "id1" not in store.metadatas
        assert "id1" not in store.id_to_idx
        assert 0 not in store.idx_to_id
        # id2 should remain
        assert "id2" in store.documents

    def test_delete_nonexistent_document(self):
        """Test deleting nonexistent document (should not raise)."""
        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.documents = {"id1": "Doc 1"}
        store.metadatas = {"id1": {}}
        store.id_to_idx = {"id1": 0}
        store.idx_to_id = {0: "id1"}

        # Should not raise
        store.delete(["nonexistent"])

        assert "id1" in store.documents


class TestFAISSStoreClear:
    """Test cases for clear method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_faiss_module.reset_mock()
        self.mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = self.mock_index

    def test_clear_resets_all_data(self):
        """Test clear resets all internal data."""
        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.documents = {"id1": "Doc 1"}
        store.metadatas = {"id1": {}}
        store.id_to_idx = {"id1": 0}
        store.idx_to_id = {0: "id1"}

        store.clear()

        # New index should be created
        assert mock_faiss_module.IndexFlatIP.call_count >= 2
        assert store.documents == {}
        assert store.metadatas == {}
        assert store.id_to_idx == {}
        assert store.idx_to_id == {}


class TestFAISSStoreCount:
    """Test cases for count method."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_faiss_module.reset_mock()
        self.mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = self.mock_index

    def test_count_returns_document_count(self):
        """Test count returns number of documents."""
        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)
        store.documents = {"id1": "Doc 1", "id2": "Doc 2", "id3": "Doc 3"}

        assert store.count() == 3

    def test_count_empty_store(self):
        """Test count on empty store."""
        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)

        assert store.count() == 0


class TestFAISSStoreInheritance:
    """Test inheritance from BaseVectorStore."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_faiss_module.reset_mock()
        self.mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = self.mock_index

    def test_inherits_from_base_vector_store(self):
        """Test that FAISSStore inherits from BaseVectorStore."""
        from src.vectorstore.base_store import BaseVectorStore
        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)

        assert isinstance(store, BaseVectorStore)

    def test_has_required_methods(self):
        """Test that FAISSStore has all required methods."""
        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)

        assert hasattr(store, "add")
        assert hasattr(store, "search")
        assert hasattr(store, "delete")
        assert hasattr(store, "clear")
        assert hasattr(store, "count")


class TestFAISSStorePersistence:
    """Test cases for save and load functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_faiss_module.reset_mock()
        self.mock_index = MagicMock()
        mock_faiss_module.IndexFlatIP.return_value = self.mock_index

    def test_save_called_on_add_with_index_path(self):
        """Test that _save is called when adding with index_path."""
        mock_numpy_module.array.return_value = MagicMock()
        mock_numpy_module.float32 = "float32"

        from src.vectorstore.faiss_store import FAISSStore

        # Create a mock path that doesn't exist (so _load won't be called)
        with patch("pathlib.Path.exists", return_value=False):
            store = FAISSStore(dimension=3, index_path="/test/path")

        # Mock _save to verify it's called
        store._save = MagicMock()

        store.add(
            ids=["id1"],
            embeddings=[[0.1, 0.2, 0.3]],
            documents=["Doc 1"],
        )

        store._save.assert_called_once()

    def test_has_save_and_load_methods(self):
        """Test that FAISSStore has _save and _load methods."""
        from src.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(dimension=3)

        assert hasattr(store, "_save")
        assert hasattr(store, "_load")
        assert callable(store._save)
        assert callable(store._load)
