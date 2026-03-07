"""Tests for base vector store."""

import pytest
from src.vectorstore.base_store import BaseVectorStore, SearchResult


class ConcreteVectorStore(BaseVectorStore):
    """Concrete implementation for testing."""

    def __init__(self):
        self.data = {}

    def add(self, ids, embeddings, documents, metadatas=None):
        for i, id in enumerate(ids):
            self.data[id] = {
                "embedding": embeddings[i],
                "document": documents[i],
                "metadata": metadatas[i] if metadatas else {},
            }

    def search(self, query_embedding, top_k=5, filter=None):
        results = []
        for id, data in list(self.data.items())[:top_k]:
            results.append(
                SearchResult(
                    content=data["document"],
                    metadata=data["metadata"],
                    score=0.9,
                    id=id,
                )
            )
        return results

    def delete(self, ids):
        for id in ids:
            self.data.pop(id, None)

    def clear(self):
        self.data.clear()

    def count(self):
        return len(self.data)


class TestSearchResult:
    """Test cases for SearchResult dataclass."""

    def test_creation(self):
        """Test SearchResult creation."""
        result = SearchResult(
            content="Test content",
            metadata={"key": "value"},
            score=0.95,
            id="doc_001",
        )

        assert result.content == "Test content"
        assert result.metadata == {"key": "value"}
        assert result.score == 0.95
        assert result.id == "doc_001"

    def test_creation_with_empty_metadata(self):
        """Test SearchResult with empty metadata."""
        result = SearchResult(
            content="Content",
            metadata={},
            score=0.5,
            id="id1",
        )

        assert result.metadata == {}

    def test_creation_with_complex_metadata(self):
        """Test SearchResult with complex metadata."""
        metadata = {
            "title": "Document Title",
            "author": "Author Name",
            "tags": ["tag1", "tag2"],
            "nested": {"key": "value"},
        }
        result = SearchResult(
            content="Content",
            metadata=metadata,
            score=0.8,
            id="id1",
        )

        assert result.metadata["title"] == "Document Title"
        assert result.metadata["tags"] == ["tag1", "tag2"]
        assert result.metadata["nested"]["key"] == "value"

    def test_score_range(self):
        """Test that score can be any float value."""
        # High score
        result1 = SearchResult(content="", metadata={}, score=1.0, id="")
        assert result1.score == 1.0

        # Zero score
        result2 = SearchResult(content="", metadata={}, score=0.0, id="")
        assert result2.score == 0.0

        # Negative score
        result3 = SearchResult(content="", metadata={}, score=-0.5, id="")
        assert result3.score == -0.5

    def test_empty_content(self):
        """Test SearchResult with empty content."""
        result = SearchResult(content="", metadata={}, score=0.5, id="id1")
        assert result.content == ""

    def test_empty_id(self):
        """Test SearchResult with empty id."""
        result = SearchResult(content="content", metadata={}, score=0.5, id="")
        assert result.id == ""


class TestBaseVectorStore:
    """Test cases for BaseVectorStore."""

    def test_add_documents(self):
        """Test adding documents to store."""
        store = ConcreteVectorStore()

        store.add(
            ids=["id1", "id2"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["Doc 1", "Doc 2"],
            metadatas=[{"key": "val1"}, {"key": "val2"}],
        )

        assert store.count() == 2

    def test_add_documents_without_metadata(self):
        """Test adding documents without metadata."""
        store = ConcreteVectorStore()

        store.add(
            ids=["id1"],
            embeddings=[[0.1, 0.2]],
            documents=["Doc 1"],
        )

        assert store.count() == 1

    def test_search_returns_list(self):
        """Test that search returns a list of SearchResult."""
        store = ConcreteVectorStore()
        store.add(
            ids=["id1"],
            embeddings=[[0.1, 0.2]],
            documents=["Doc 1"],
        )

        results = store.search([0.1, 0.2])

        assert isinstance(results, list)
        assert all(isinstance(r, SearchResult) for r in results)

    def test_search_respects_top_k(self):
        """Test that search respects top_k parameter."""
        store = ConcreteVectorStore()
        for i in range(10):
            store.add(
                ids=[f"id{i}"],
                embeddings=[[0.1 * i, 0.2 * i]],
                documents=[f"Doc {i}"],
            )

        results = store.search([0.1, 0.2], top_k=3)

        assert len(results) <= 3

    def test_delete_documents(self):
        """Test deleting documents from store."""
        store = ConcreteVectorStore()
        store.add(
            ids=["id1", "id2", "id3"],
            embeddings=[[0.1], [0.2], [0.3]],
            documents=["Doc 1", "Doc 2", "Doc 3"],
        )

        store.delete(["id1", "id2"])

        assert store.count() == 1

    def test_delete_nonexistent_document(self):
        """Test deleting nonexistent document (should not raise)."""
        store = ConcreteVectorStore()
        store.add(
            ids=["id1"],
            embeddings=[[0.1]],
            documents=["Doc 1"],
        )

        # Should not raise
        store.delete(["nonexistent"])

        assert store.count() == 1

    def test_clear_store(self):
        """Test clearing all documents from store."""
        store = ConcreteVectorStore()
        store.add(
            ids=["id1", "id2"],
            embeddings=[[0.1], [0.2]],
            documents=["Doc 1", "Doc 2"],
        )

        store.clear()

        assert store.count() == 0

    def test_count_empty_store(self):
        """Test count on empty store."""
        store = ConcreteVectorStore()

        assert store.count() == 0

    def test_abstract_methods_must_be_implemented(self):
        """Test that abstract methods must be implemented."""

        class IncompleteStore(BaseVectorStore):
            pass

        with pytest.raises(TypeError):
            IncompleteStore()

    def test_partial_implementation_raises(self):
        """Test that partial implementation raises TypeError."""

        class PartialStore(BaseVectorStore):
            def add(self, ids, embeddings, documents, metadatas=None):
                pass

            def search(self, query_embedding, top_k=5, filter=None):
                pass

            # Missing delete, clear, count

        with pytest.raises(TypeError):
            PartialStore()
