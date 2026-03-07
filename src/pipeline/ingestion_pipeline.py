"""Ingestion pipeline for processing documents."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 파이프라인은 문서를 가져오고(크롤), 정리(클린/정규화), 잘라서(청크), 임베딩을 만들고
#   벡터 저장소에 넣는 전체 과정을 하나로 묶어 자동화해요.
# 주요 포인트:
# - 단계: 크롤링 -> 정리/정규화 -> 청킹 -> 임베딩 생성 -> 저장
# - 각 단계에서 실패하면 오류를 모아서 리포트합니다.

from typing import Any
from dataclasses import dataclass

from ..crawler.base_crawler import BaseCrawler, Document
from ..preprocessor.cleaner import TextCleaner
from ..preprocessor.normalizer import TextNormalizer
from ..chunker.base_chunker import BaseChunker, Chunk
from ..embedder.base_embedder import BaseEmbedder
from ..vectorstore.base_store import BaseVectorStore


@dataclass
class IngestionResult:
    """Ingestion pipeline result."""

    documents_processed: int
    chunks_created: int
    embeddings_generated: int
    errors: list[str]


class IngestionPipeline:
    """Pipeline for ingesting documents into vector store."""

    def __init__(
        self,
        crawler: BaseCrawler,
        chunker: BaseChunker,
        embedder: BaseEmbedder,
        vectorstore: BaseVectorStore,
        cleaner: TextCleaner | None = None,
        normalizer: TextNormalizer | None = None,
    ):
        """
        Initialize ingestion pipeline.

        Args:
            crawler: Document crawler
            chunker: Text chunker
            embedder: Text embedder
            vectorstore: Vector store
            cleaner: Optional text cleaner
            normalizer: Optional text normalizer
        """
        self.crawler = crawler
        self.chunker = chunker
        self.embedder = embedder
        self.vectorstore = vectorstore
        self.cleaner = cleaner or TextCleaner()
        self.normalizer = normalizer or TextNormalizer()

    def ingest(
        self,
        sources: list[str],
        batch_size: int = 100,
    ) -> IngestionResult:
        """
        Ingest documents from sources.

        Args:
            sources: List of source URLs or paths
            batch_size: Batch size for embedding

        Returns:
            IngestionResult with statistics
        """
        errors = []
        all_chunks = []

        # Step 1: Crawl documents
        print(f"Crawling {len(sources)} sources...")
        documents = self.crawler.crawl_multiple(sources)
        print(f"Crawled {len(documents)} documents")

        # Step 2: Preprocess and chunk
        print("Processing and chunking documents...")
        for doc in documents:
            try:
                # Clean and normalize text
                text = self.cleaner.clean(doc.content)
                text = self.normalizer.normalize(text)

                # Chunk text
                chunks = self.chunker.chunk(text, source=doc.source)

                # Add document metadata to chunks
                for chunk in chunks:
                    chunk.metadata.update(doc.metadata)

                all_chunks.extend(chunks)

            except Exception as e:
                errors.append(f"Error processing {doc.source}: {e}")

        print(f"Created {len(all_chunks)} chunks")

        # Step 3: Generate embeddings and store
        print("Generating embeddings...")
        self._store_chunks(all_chunks, batch_size)

        return IngestionResult(
            documents_processed=len(documents),
            chunks_created=len(all_chunks),
            embeddings_generated=len(all_chunks),
            errors=errors,
        )

    def _store_chunks(self, chunks: list[Chunk], batch_size: int) -> None:
        """Store chunks in vector store."""
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            ids = [chunk.chunk_id for chunk in batch]
            texts = [chunk.content for chunk in batch]
            metadatas = [chunk.metadata for chunk in batch]

            # Generate embeddings
            embeddings = self.embedder.embed_batch(texts)

            # Store in vector store
            self.vectorstore.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

            print(f"Stored {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")

    def ingest_single(self, source: str) -> IngestionResult:
        """
        Ingest a single document.

        Args:
            source: Source URL or path

        Returns:
            IngestionResult
        """
        return self.ingest([source])
