"""Script to run data ingestion pipeline."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 스크립트는 콘솔에서 실행되어 문서를 불러오고(IngestionPipeline) 벡터 저장소에 넣는 전체 흐름을 실행합니다.
# 주요 포인트:
# - `--sources`로 파일 경로나 URL을 넣으면 해당 소스를 순회해서 처리합니다.
# - 설정은 `config.settings`에서 가져와 기본값으로 사용합니다.

import argparse
from pathlib import Path

from config.settings import settings
from src.crawler.web_crawler import WebCrawler
from src.crawler.file_loader import FileLoader
from src.preprocessor.cleaner import TextCleaner
from src.preprocessor.normalizer import TextNormalizer
from src.chunker.recursive_chunker import RecursiveChunker
from src.embedder import create_embedder
from src.vectorstore.chroma_store import ChromaStore
from src.pipeline.ingestion_pipeline import IngestionPipeline


def main():
    """Run ingestion pipeline."""
    parser = argparse.ArgumentParser(description="Run RAG ingestion pipeline")
    parser.add_argument(
        "--sources",
        nargs="+",
        required=True,
        help="Source URLs or file paths to ingest",
    )
    parser.add_argument(
        "--source-type",
        choices=["web", "file"],
        default="file",
        help="Type of sources (web or file)",
    )
    parser.add_argument(
        "--collection",
        default="rag_collection",
        help="Vector store collection name",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=settings.CHUNK_SIZE,
        help="Chunk size for text splitting",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=settings.CHUNK_OVERLAP,
        help="Chunk overlap for text splitting",
    )
    parser.add_argument(
        "--embedder",
        type=str,
        default=settings.EMBEDDER_TYPE,
        choices=["openai", "huggingface", "bge-m3"],
        help="Embedder type (default: from settings)",
    )
    args = parser.parse_args()

    # Initialize components
    if args.source_type == "web":
        crawler = WebCrawler()
    else:
        crawler = FileLoader()

    cleaner = TextCleaner()
    normalizer = TextNormalizer()
    chunker = RecursiveChunker(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"Initializing embedder: {args.embedder}")
    embedder = create_embedder(args.embedder)
    vectorstore = ChromaStore(
        collection_name=args.collection,
        persist_directory=settings.VECTORDB_DIR,
    )

    # Create pipeline
    pipeline = IngestionPipeline(
        crawler=crawler,
        chunker=chunker,
        embedder=embedder,
        vectorstore=vectorstore,
        cleaner=cleaner,
        normalizer=normalizer,
    )

    # Run ingestion
    print(f"Starting ingestion of {len(args.sources)} sources...")
    result = pipeline.ingest(args.sources)

    # Print results
    print("\n=== Ingestion Complete ===")
    print(f"Documents processed: {result.documents_processed}")
    print(f"Chunks created: {result.chunks_created}")
    print(f"Embeddings generated: {result.embeddings_generated}")

    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
