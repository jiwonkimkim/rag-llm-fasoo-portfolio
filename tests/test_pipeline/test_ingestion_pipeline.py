"""Tests for ingestion pipeline."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 파일은 IngestionPipeline이 문서를 잘 수집하고(크롤), 처리(전처리/청킹), 임베딩을 생성해
#   저장하는 전체 흐름을 올바르게 수행하는지 검사합니다.
# 주요 포인트:
# - 다양한 상황(단일 문서, 다중 문서, 전처리 실패 등)에 대한 테스트가 포함되어 있습니다.

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.crawler.base_crawler import BaseCrawler, Document
from src.chunker.base_chunker import BaseChunker, Chunk
from src.embedder.base_embedder import BaseEmbedder
from src.vectorstore.base_store import BaseVectorStore
from src.pipeline.ingestion_pipeline import IngestionPipeline, IngestionResult


class MockCrawler(BaseCrawler):
    """Mock crawler for testing."""

    def __init__(self, documents: list[Document] | None = None):
        self.documents = documents or []

    def crawl(self, source: str) -> list[Document]:
        return [doc for doc in self.documents if doc.source == source]

    def crawl_multiple(self, sources: list[str]) -> list[Document]:
        return self.documents


class MockChunker(BaseChunker):
    """Mock chunker for testing."""

    def chunk(self, text: str, source: str = "") -> list[Chunk]:
        return [
            Chunk(
                content=text,
                metadata={"chunk_index": 0},
                chunk_id=self._generate_chunk_id(source, 0),
                source=source,
            )
        ]


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

    def __init__(self):
        self.documents = []

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict] | None = None,
    ) -> None:
        self.documents.extend(documents)

    def search(self, query_embedding, top_k=5, filter=None):
        return []

    def delete(self, ids: list[str]) -> None:
        pass

    def clear(self) -> None:
        self.documents = []

    def count(self) -> int:
        return len(self.documents)


class TestIngestionResult:
    """Test cases for IngestionResult dataclass."""

    def test_creation(self):
        """Test IngestionResult creation."""
        result = IngestionResult(
            documents_processed=5,
            chunks_created=10,
            embeddings_generated=10,
            errors=["error1"],
        )

        assert result.documents_processed == 5
        assert result.chunks_created == 10
        assert result.embeddings_generated == 10
        assert result.errors == ["error1"]

    def test_empty_errors(self):
        """Test IngestionResult with no errors."""
        result = IngestionResult(
            documents_processed=3,
            chunks_created=6,
            embeddings_generated=6,
            errors=[],
        )

        assert result.errors == []


class TestIngestionPipeline:
    """Test cases for IngestionPipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.documents = [
            Document(
                content="Test document content",
                metadata={"title": "Test"},
                source="test_source.txt",
            )
        ]
        self.crawler = MockCrawler(self.documents)
        self.chunker = MockChunker()
        self.embedder = MockEmbedder()
        self.vectorstore = MockVectorStore()

    def test_initialization(self):
        """Test pipeline initialization."""
        pipeline = IngestionPipeline(
            crawler=self.crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=self.vectorstore,
        )

        assert pipeline.crawler == self.crawler
        assert pipeline.chunker == self.chunker
        assert pipeline.embedder == self.embedder
        assert pipeline.vectorstore == self.vectorstore
        assert pipeline.cleaner is not None
        assert pipeline.normalizer is not None

    def test_initialization_with_custom_preprocessors(self):
        """Test pipeline initialization with custom preprocessors."""
        mock_cleaner = Mock()
        mock_normalizer = Mock()

        pipeline = IngestionPipeline(
            crawler=self.crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=self.vectorstore,
            cleaner=mock_cleaner,
            normalizer=mock_normalizer,
        )

        assert pipeline.cleaner == mock_cleaner
        assert pipeline.normalizer == mock_normalizer

    def test_ingest_single_document(self):
        """Test ingesting a single document."""
        pipeline = IngestionPipeline(
            crawler=self.crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=self.vectorstore,
        )

        result = pipeline.ingest(["test_source.txt"])

        assert result.documents_processed == 1
        assert result.chunks_created == 1
        assert result.embeddings_generated == 1
        assert result.errors == []

    def test_ingest_multiple_documents(self):
        """Test ingesting multiple documents."""
        documents = [
            Document(content="Doc 1", metadata={}, source="source1.txt"),
            Document(content="Doc 2", metadata={}, source="source2.txt"),
            Document(content="Doc 3", metadata={}, source="source3.txt"),
        ]
        crawler = MockCrawler(documents)

        pipeline = IngestionPipeline(
            crawler=crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=self.vectorstore,
        )

        result = pipeline.ingest(["source1.txt", "source2.txt", "source3.txt"])

        assert result.documents_processed == 3
        assert result.chunks_created == 3

    def test_ingest_with_preprocessing(self):
        """Test that preprocessing is applied."""
        mock_cleaner = Mock()
        mock_cleaner.clean.return_value = "cleaned text"
        mock_normalizer = Mock()
        mock_normalizer.normalize.return_value = "normalized text"

        pipeline = IngestionPipeline(
            crawler=self.crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=self.vectorstore,
            cleaner=mock_cleaner,
            normalizer=mock_normalizer,
        )

        pipeline.ingest(["test_source.txt"])

        mock_cleaner.clean.assert_called_once()
        mock_normalizer.normalize.assert_called_once_with("cleaned text")

    def test_ingest_adds_document_metadata_to_chunks(self):
        """Test that document metadata is added to chunks."""
        documents = [
            Document(
                content="Test content",
                metadata={"author": "Test Author", "date": "2024-01-01"},
                source="test.txt",
            )
        ]
        crawler = MockCrawler(documents)

        # Custom chunker that preserves metadata
        class MetadataChunker(BaseChunker):
            def chunk(self, text: str, source: str = "") -> list[Chunk]:
                return [
                    Chunk(
                        content=text,
                        metadata={"chunk_index": 0},
                        chunk_id="test_id",
                        source=source,
                    )
                ]

        chunker = MetadataChunker()
        vectorstore = Mock(spec=BaseVectorStore)

        pipeline = IngestionPipeline(
            crawler=crawler,
            chunker=chunker,
            embedder=self.embedder,
            vectorstore=vectorstore,
        )

        pipeline.ingest(["test.txt"])

        # Verify metadata was passed to vectorstore
        vectorstore.add.assert_called_once()
        call_args = vectorstore.add.call_args
        metadatas = call_args.kwargs.get("metadatas") or call_args[1].get("metadatas")

        assert metadatas is not None
        assert "author" in metadatas[0]
        assert metadatas[0]["author"] == "Test Author"

    def test_ingest_handles_processing_error(self):
        """Test error handling during document processing."""
        mock_cleaner = Mock()
        mock_cleaner.clean.side_effect = Exception("Cleaning error")

        pipeline = IngestionPipeline(
            crawler=self.crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=self.vectorstore,
            cleaner=mock_cleaner,
        )

        result = pipeline.ingest(["test_source.txt"])

        assert len(result.errors) == 1
        assert "Cleaning error" in result.errors[0]

    def test_ingest_with_batch_size(self):
        """Test batch processing of embeddings."""
        # Create multiple documents to test batching
        documents = [
            Document(content=f"Doc {i}", metadata={}, source=f"source{i}.txt")
            for i in range(5)
        ]
        crawler = MockCrawler(documents)

        mock_embedder = Mock(spec=BaseEmbedder)
        mock_embedder.embed_batch.return_value = [[0.1, 0.2, 0.3] for _ in range(2)]

        pipeline = IngestionPipeline(
            crawler=crawler,
            chunker=self.chunker,
            embedder=mock_embedder,
            vectorstore=self.vectorstore,
        )

        pipeline.ingest(["source0.txt"], batch_size=2)

        # embed_batch should be called for each batch
        assert mock_embedder.embed_batch.called

    def test_ingest_single(self):
        """Test ingest_single convenience method."""
        pipeline = IngestionPipeline(
            crawler=self.crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=self.vectorstore,
        )

        result = pipeline.ingest_single("test_source.txt")

        assert isinstance(result, IngestionResult)
        assert result.documents_processed == 1

    def test_ingest_empty_sources(self):
        """Test ingestion with empty sources list."""
        crawler = MockCrawler([])

        pipeline = IngestionPipeline(
            crawler=crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=self.vectorstore,
        )

        result = pipeline.ingest([])

        assert result.documents_processed == 0
        assert result.chunks_created == 0
        assert result.errors == []

    def test_store_chunks_batching(self):
        """Test _store_chunks method batches correctly."""
        mock_vectorstore = Mock(spec=BaseVectorStore)

        pipeline = IngestionPipeline(
            crawler=self.crawler,
            chunker=self.chunker,
            embedder=self.embedder,
            vectorstore=mock_vectorstore,
        )

        chunks = [
            Chunk(content=f"chunk{i}", metadata={}, chunk_id=f"id{i}", source="test")
            for i in range(5)
        ]

        pipeline._store_chunks(chunks, batch_size=2)

        # Should be called 3 times: 2 + 2 + 1
        assert mock_vectorstore.add.call_count == 3
