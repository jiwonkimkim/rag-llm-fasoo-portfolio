"""
ChromaDB 기반 벡터 저장소 구현

이 구현체는 `BaseVectorStore` 추상화에 맞춰 ChromaDB 클라이언트를 래핑합니다.
`persist_directory`를 지정하면 영속 저장 모드를 사용하며, 그렇지 않으면 인메모리 클라이언트를 사용합니다.

주의사항:
- 외부 패키지(`chromadb`)에 대한 의존성이 있으므로 런타임에 해당 패키지가 설치되어 있어야 합니다.
  테스트 환경에서는 지연 import(생성자 내부의 import)를 통해 의존성 문제를 완화합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - ChromaDB라는 서비스(또는 라이브러리)를 사용해 벡터를 저장하고 검색하는 방법을 제공해요.
# 주요 포인트:
# - persist_directory를 지정하면 데이터가 디스크에 남아서 재시작 후에도 보존돼요.
# - search는 Chroma의 쿼리 결과를 `SearchResult` 객체로 바꿔서 반환해요.

from typing import Any
from pathlib import Path

from .base_store import BaseVectorStore, SearchResult


class ChromaStore(BaseVectorStore):
    """ChromaDB 기반 벡터 저장소 래퍼.

    구성:
    - `collection_name`: 해당 저장소에서 사용할 컬렉션 이름
    - `persist_directory`: 디스크 기반 영속 저장 경로
    """

    def __init__(
        self,
        collection_name: str = "rag_collection",
        persist_directory: str | Path | None = None,
    ):
        """초기화: 내부적으로 chromadb 클라이언트를 생성합니다."""
        import chromadb

        self.persist_directory = Path(persist_directory) if persist_directory else None

        if persist_directory:
            self.client = chromadb.PersistentClient(path=str(persist_directory))
        else:
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """문서 및 임베딩을 컬렉션에 추가합니다."""
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """쿼리 임베딩과 유사한 상위 결과를 반환합니다."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter,
            include=["documents", "metadatas", "distances"],
        )

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, id in enumerate(results["ids"][0]):
                search_results.append(
                    SearchResult(
                        content=results["documents"][0][i] if results["documents"] else "",
                        metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                        score=1 - results["distances"][0][i] if results["distances"] else 0,
                        id=id,
                    )
                )

        return search_results

    def delete(self, ids: list[str]) -> None:
        """주어진 ID 목록을 삭제합니다."""
        self.collection.delete(ids=ids)

    def clear(self) -> None:
        """컬렉션을 삭제하고 동일 이름의 새 컬렉션을 생성하여 초기화합니다."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"},
        )

    def delete_collection(self) -> None:
        """컬렉션을 완전히 삭제합니다 (재생성하지 않음, 디렉토리도 삭제)."""
        import shutil

        self.client.delete_collection(self.collection.name)
        self.collection = None

        # Delete the persist directory if it exists
        if self.persist_directory and self.persist_directory.exists():
            shutil.rmtree(self.persist_directory)

    def count(self) -> int:
        """컬렉션 내 문서 수를 반환합니다."""
        return self.collection.count()
