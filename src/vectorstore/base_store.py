"""Base vector store class."""

# 이해가게 개념설명 알기쉽게 핵심 설명(자세 설명):
# 목적:
# - 이 파일은 '벡터 저장소'가 어떤 기능을 가져야 하는지 규칙을 알려주는 설계도예요.
# 주요 포인트:
# - 구현체(예: FAISS, Chroma, Pinecone)는 이 규칙을 따르게 되어 있어요.
# - add: 벡터와 문서를 저장하는 방법, search: 임베딩으로 비슷한 문서를 찾는 방법을 정의합니다.
# - delete/clear/count는 저장소를 관리하는 기능이에요.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SearchResult:
    """Search result data class."""

    content: str
    metadata: dict[str, Any]
    score: float
    id: str


class BaseVectorStore(ABC):
    """벡터 저장소의 추상 베이스 클래스.

    구현체는 다음 책임을 가져야 합니다:
    - 벡터 및 메타데이터 저장(`add`)
    - 임베딩 기반 검색(`search`)

    메서드 시그니처는 일반적인 사용 사례를 포괄하도록 설계되었습니다.
    """

    @abstractmethod
    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """벡터와 메타데이터를 저장소에 추가합니다.

        Args:
            embeddings: 벡터(또는 벡터 목록)
            metadatas: 각 벡터에 대응되는 메타데이터 목록
            ids: 선택적 식별자 목록
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """주어진 임베딩과 유사한 상위 `top_k` 결과를 반환합니다.

        반환값은 구현체별로 다를 수 있으나 일반적으로 각 결과는
        `{'id': ..., 'score': ..., 'metadata': ..., 'content': ...}` 형태를 따릅니다.
        """
        pass

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        """
        Delete documents by ID.

        Args:
            ids: List of document IDs to delete
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from the store."""
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get number of documents in store.

        Returns:
            Document count
        """
        pass
