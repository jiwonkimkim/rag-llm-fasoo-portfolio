"""
Pinecone 벡터 저장소 구현

Pinecone 클라이언트를 래핑하여 벡터 업서트, 검색, 삭제, 카운트 등의 기능을 제공합니다.

주의사항:
- Pinecone SDK 의존성이 필요합니다. 생성자 내부에서 지연 import를 사용하여 테스트 시 안전하게 동작하도록 합니다.
"""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - Pinecone이라는 외부 서비스를 사용해 벡터를 저장하고 빠르게 검색하는 방법을 구현해요.
# 주요 포인트:
# - add: 문서와 벡터를 배치로 업서트해요.
# - search: 결과의 metadata에서 원문(text)을 꺼내서 `SearchResult`로 만듭니다.
# - delete/clear/count: 저장소 관리 기능을 제공합니다.

from typing import Any

from .base_store import BaseVectorStore, SearchResult


class PineconeStore(BaseVectorStore):
    """Pinecone 기반 벡터 저장소 래퍼.

    인스턴스는 지정된 `index_name`의 인덱스를 사용하며, `namespace`로 논리적 분리도 가능합니다.
    """

    def __init__(
        self,
        index_name: str,
        api_key: str | None = None,
        environment: str = "gcp-starter",
        namespace: str = "",
    ):
        """초기화: Pinecone 클라이언트를 생성하고 인덱스 핸들을 가져옵니다."""
        from pinecone import Pinecone

        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.namespace = namespace

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """문서와 메타데이터를 벡터와 함께 업서트합니다. 배치 단위로 전송합니다."""
        vectors = []
        for i, id in enumerate(ids):
            metadata = metadatas[i] if metadatas else {}
            metadata["text"] = documents[i]

            vectors.append({
                "id": id,
                "values": embeddings[i],
                "metadata": metadata,
            })

        # 배치 업서트로 대량 추가 처리
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch, namespace=self.namespace)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """쿼리 임베딩으로 Pinecone에서 유사 항목을 검색합니다."""
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter,
            include_metadata=True,
            namespace=self.namespace,
        )

        search_results = []
        for match in results.matches:
            metadata = match.metadata or {}
            content = metadata.pop("text", "")

            search_results.append(
                SearchResult(
                    content=content,
                    metadata=metadata,
                    score=match.score,
                    id=match.id,
                )
            )

        return search_results

    def delete(self, ids: list[str]) -> None:
        """주어진 ID 목록을 삭제합니다."""
        self.index.delete(ids=ids, namespace=self.namespace)

    def clear(self) -> None:
        """네임스페이스 내 모든 벡터를 삭제합니다."""
        self.index.delete(delete_all=True, namespace=self.namespace)

    def count(self) -> int:
        """인덱스의 벡터 수를 반환합니다(네임스페이스가 지정된 경우 해당 네임스페이스의 수)."""
        stats = self.index.describe_index_stats()
        if self.namespace:
            return stats.namespaces.get(self.namespace, {}).get("vector_count", 0)
        return stats.total_vector_count
