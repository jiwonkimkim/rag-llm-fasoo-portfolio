"""Script to run RAG query pipeline."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 스크립트는 콘솔에서 질문을 받아 RAG 파이프라인을 실행하고 답을 출력합니다.
# 주요 포인트:
# - `--interactive` 모드를 사용하면 대화형으로 여러 질문을 할 수 있어요.
# - 모델 설정은 `config.settings`에서 불러옵니다.

import argparse

from config.settings import settings
from src.embedder import create_embedder
from src.vectorstore.chroma_store import ChromaStore
from src.retriever.dense_retriever import DenseRetriever
from src.generator.llm_client import LLMClient
from src.generator.prompt_builder import PromptBuilder
from src.pipeline.rag_pipeline import RAGPipeline


def main():
    """Run RAG query pipeline."""
    parser = argparse.ArgumentParser(description="Run RAG query")
    parser.add_argument(
        "--query",
        type=str,
        help="Question to ask",
    )
    parser.add_argument(
        "--collection",
        default="rag_collection",
        help="Vector store collection name",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=settings.TOP_K,
        help="Number of documents to retrieve",
    )
    parser.add_argument(
        "--embedder",
        type=str,
        default=settings.EMBEDDER_TYPE,
        choices=["openai", "huggingface", "bge-m3"],
        help="Embedder type (default: from settings)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode",
    )
    args = parser.parse_args()

    # Initialize components
    print(f"Initializing embedder: {args.embedder}")
    embedder = create_embedder(args.embedder)
    vectorstore = ChromaStore(
        collection_name=args.collection,
        persist_directory=settings.VECTORDB_DIR,
    )
    retriever = DenseRetriever(
        embedder=embedder,
        vectorstore=vectorstore,
        top_k=args.top_k,
    )
    llm_client = LLMClient(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
    )
    prompt_builder = PromptBuilder()

    # Create pipeline
    pipeline = RAGPipeline(
        retriever=retriever,
        llm_client=llm_client,
        prompt_builder=prompt_builder,
    )

    if args.interactive:
        print("RAG Interactive Mode (type 'exit' to quit)")
        print("=" * 50)

        while True:
            query = input("\nQuestion: ").strip()
            if query.lower() == "exit":
                break

            if not query:
                continue

            response = pipeline.query(query)
            print(f"\nAnswer: {response.answer}")
            print(f"\nSources: {', '.join(response.sources)}")
            print(f"Confidence: {response.confidence:.2f}" if response.confidence else "")

    elif args.query:
        response = pipeline.query(args.query)
        print(f"\nQuestion: {args.query}")
        print(f"\nAnswer: {response.answer}")
        print(f"\nSources: {', '.join(response.sources)}")
        if response.confidence:
            print(f"Confidence: {response.confidence:.2f}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
